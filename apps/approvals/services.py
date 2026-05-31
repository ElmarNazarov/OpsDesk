from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import GROUP_HR, GROUP_OPS
from apps.approvals.models import (
    ApprovalAction,
    ApprovalActionType,
    ApprovalStep,
    ApprovalStepStatus,
    RoleRequired,
)
from apps.approvals.permissions import user_can_approve_request, user_can_reject_request
from apps.audit.models import AuditAction
from apps.audit.services import audit_log
from apps.core.exceptions import InvalidStateError, PermissionDeniedError
from apps.notifications.models import NotificationType
from apps.notifications.services import create_notification
from apps.requests.models import Request, RequestStatus, RequestStatusHistory


def _get_policy_flags(request_obj):
    policy = getattr(request_obj.category, "approval_policy", None)
    if policy and policy.is_active:
        return (
            policy.requires_manager_approval,
            policy.requires_ops_approval,
            policy.requires_hr_approval,
        )
    cat = request_obj.category
    return (
        cat.requires_manager_approval,
        cat.requires_ops_approval,
        cat.requires_hr_approval,
    )


def _resolve_approver(request_obj, role_required: str):
    requester_profile = getattr(request_obj.requester, "profile", None)
    if role_required == RoleRequired.MANAGER:
        if requester_profile and requester_profile.manager_id:
            return requester_profile.manager
        if request_obj.department and request_obj.department.manager_id:
            return request_obj.department.manager
    if role_required == RoleRequired.OPS:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(groups__name=GROUP_OPS, is_active=True).first()
    if role_required == RoleRequired.HR:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(groups__name=GROUP_HR, is_active=True).first()
    return None


@transaction.atomic
def create_approval_steps_for_request(request_obj):
    ApprovalStep.objects.filter(request=request_obj).delete()
    req_mgr, req_ops, req_hr = _get_policy_flags(request_obj)
    steps_config = []
    order = 1
    if req_mgr:
        steps_config.append((order, RoleRequired.MANAGER))
        order += 1
    if req_ops:
        steps_config.append((order, RoleRequired.OPS))
        order += 1
    if req_hr:
        steps_config.append((order, RoleRequired.HR))

    first_pending_approver = None
    for step_order, role in steps_config:
        approver = _resolve_approver(request_obj, role)
        status = ApprovalStepStatus.PENDING if approver else ApprovalStepStatus.SKIPPED
        ApprovalStep.objects.create(
            request=request_obj,
            step_order=step_order,
            approver=approver,
            role_required=role,
            status=status,
        )
        if status == ApprovalStepStatus.PENDING and first_pending_approver is None:
            first_pending_approver = approver

    request_obj.current_approver = first_pending_approver
    request_obj.save(update_fields=["current_approver", "updated_at"])
    return request_obj.approval_steps.all()


def get_next_approval_step(request_obj):
    return (
        request_obj.approval_steps.filter(status=ApprovalStepStatus.PENDING)
        .order_by("step_order")
        .first()
    )


def _record_status(request_obj, actor, from_status, to_status, reason=""):
    RequestStatusHistory.objects.create(
        request=request_obj,
        from_status=from_status,
        to_status=to_status,
        changed_by=actor,
        reason=reason,
    )


def _needs_ops_processing(request_obj) -> bool:
    cat = request_obj.category
    return cat.slug in ("equipment", "software-access") or cat.requires_ops_approval


@transaction.atomic
def approve_request(actor, request_obj, comment="", http_request=None):
    if not user_can_approve_request(actor, request_obj):
        raise PermissionDeniedError("Cannot approve this request.")

    request_obj = Request.objects.select_for_update().get(pk=request_obj.pk)
    step = get_next_approval_step(request_obj)
    if not step:
        raise InvalidStateError("No pending approval step.")

    old_status = request_obj.status
    step.status = ApprovalStepStatus.APPROVED
    step.decided_at = timezone.now()
    step.save(update_fields=["status", "decided_at", "updated_at"])

    ApprovalAction.objects.create(
        request=request_obj,
        step=step,
        actor=actor,
        action=ApprovalActionType.APPROVE,
        comment=comment,
    )

    next_step = get_next_approval_step(request_obj)
    if next_step:
        request_obj.current_approver = next_step.approver
        request_obj.status = RequestStatus.IN_REVIEW
        request_obj.save(update_fields=["current_approver", "status", "updated_at"])
        _record_status(request_obj, actor, old_status, RequestStatus.IN_REVIEW, comment)
    else:
        if _needs_ops_processing(request_obj):
            request_obj.status = RequestStatus.OPS_PROCESSING
            from django.contrib.auth import get_user_model

            User = get_user_model()
            ops_user = User.objects.filter(groups__name=GROUP_OPS, is_active=True).first()
            request_obj.current_approver = ops_user
        else:
            request_obj.status = RequestStatus.APPROVED
            request_obj.current_approver = None
        request_obj.save(update_fields=["status", "current_approver", "updated_at"])
        _record_status(request_obj, actor, old_status, request_obj.status, comment)

    audit_log(actor, AuditAction.REQUEST_APPROVED, entity=request_obj, request=http_request)
    create_notification(
        recipient=request_obj.requester,
        title=f"Request approved: {request_obj.public_id}",
        message=f"Your request '{request_obj.title}' was approved.",
        notification_type=NotificationType.REQUEST_APPROVED,
        related_request=request_obj,
    )
    return request_obj


@transaction.atomic
def reject_request(actor, request_obj, comment="", http_request=None):
    if not user_can_reject_request(actor, request_obj):
        raise PermissionDeniedError("Cannot reject this request.")

    request_obj = Request.objects.select_for_update().get(pk=request_obj.pk)
    step = get_next_approval_step(request_obj)
    if not step:
        raise InvalidStateError("No pending approval step.")

    old_status = request_obj.status
    step.status = ApprovalStepStatus.REJECTED
    step.decided_at = timezone.now()
    step.save(update_fields=["status", "decided_at", "updated_at"])

    ApprovalAction.objects.create(
        request=request_obj,
        step=step,
        actor=actor,
        action=ApprovalActionType.REJECT,
        comment=comment,
    )

    request_obj.status = RequestStatus.REJECTED
    request_obj.current_approver = None
    request_obj.resolved_at = timezone.now()
    request_obj.save(update_fields=["status", "current_approver", "resolved_at", "updated_at"])
    _record_status(request_obj, actor, old_status, RequestStatus.REJECTED, comment)
    audit_log(actor, AuditAction.REQUEST_REJECTED, entity=request_obj, request=http_request)
    create_notification(
        recipient=request_obj.requester,
        title=f"Request rejected: {request_obj.public_id}",
        message=f"Your request '{request_obj.title}' was rejected. {comment}",
        notification_type=NotificationType.REQUEST_REJECTED,
        related_request=request_obj,
    )
    return request_obj


@transaction.atomic
def return_request_for_changes(actor, request_obj, comment="", http_request=None):
    if not user_can_approve_request(actor, request_obj):
        raise PermissionDeniedError("Cannot return this request.")

    request_obj = Request.objects.select_for_update().get(pk=request_obj.pk)
    step = get_next_approval_step(request_obj)
    if step:
        ApprovalAction.objects.create(
            request=request_obj,
            step=step,
            actor=actor,
            action=ApprovalActionType.RETURN_FOR_CHANGES,
            comment=comment,
        )
    old_status = request_obj.status
    request_obj.status = RequestStatus.DRAFT
    request_obj.current_approver = None
    request_obj.save(update_fields=["status", "current_approver", "updated_at"])
    request_obj.approval_steps.all().delete()
    _record_status(request_obj, actor, old_status, RequestStatus.DRAFT, comment)
    create_notification(
        recipient=request_obj.requester,
        title=f"Changes requested: {request_obj.public_id}",
        message=f"Please update your request. {comment}",
        notification_type=NotificationType.REQUEST_COMMENTED,
        related_request=request_obj,
    )
    return request_obj

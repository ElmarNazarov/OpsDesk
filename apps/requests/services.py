from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import audit_log
from apps.core.exceptions import InvalidStateError, PermissionDeniedError
from apps.notifications.models import NotificationType
from apps.notifications.services import create_notification
from apps.requests.constants import FINAL_STATUSES
from apps.requests.models import Request, RequestComment, RequestStatus, RequestStatusHistory
from apps.requests.permissions import (
    require_can_view_request,
    user_can_cancel_request,
    user_can_comment_on_request,
    user_can_submit_request,
)
from apps.requests.selectors import generate_public_id


def _record_status_history(request_obj, actor, from_status, to_status, reason=""):
    RequestStatusHistory.objects.create(
        request=request_obj,
        from_status=from_status,
        to_status=to_status,
        changed_by=actor,
        reason=reason,
    )


@transaction.atomic
def create_request(actor, *, title, description, category, priority, metadata=None):
    profile = getattr(actor, "profile", None)
    department = profile.department if profile else None
    public_id = generate_public_id()
    request_obj = Request.objects.create(
        public_id=public_id,
        title=title,
        description=description,
        category=category,
        requester=actor,
        department=department,
        priority=priority,
        status=RequestStatus.DRAFT,
        metadata=metadata or {},
    )
    audit_log(actor, AuditAction.REQUEST_CREATED, entity=request_obj)
    _record_status_history(request_obj, actor, "", RequestStatus.DRAFT)
    return request_obj


@transaction.atomic
def submit_request(actor, request_obj, http_request=None):
    if not user_can_submit_request(actor, request_obj):
        raise PermissionDeniedError("Cannot submit this request.")
    if request_obj.status != RequestStatus.DRAFT:
        raise InvalidStateError("Only draft requests can be submitted.")

    from apps.approvals.services import create_approval_steps_for_request

    old_status = request_obj.status
    category = request_obj.category
    needs_approval = (
        category.requires_manager_approval
        or category.requires_ops_approval
        or category.requires_hr_approval
    )

    if needs_approval:
        request_obj.status = RequestStatus.IN_REVIEW
    else:
        request_obj.status = RequestStatus.SUBMITTED

    request_obj.submitted_at = timezone.now()
    request_obj.save(update_fields=["status", "submitted_at", "updated_at"])

    if needs_approval:
        create_approval_steps_for_request(request_obj)

    _record_status_history(request_obj, actor, old_status, request_obj.status, "Submitted")
    audit_log(actor, AuditAction.REQUEST_SUBMITTED, entity=request_obj, request=http_request)

    manager = None
    if hasattr(actor, "profile") and actor.profile.manager_id:
        manager = actor.profile.manager
    elif request_obj.department and request_obj.department.manager_id:
        manager = request_obj.department.manager

    if manager:
        create_notification(
            recipient=manager,
            title=f"New request: {request_obj.public_id}",
            message=f"{actor.full_name} submitted {request_obj.title}",
            notification_type=NotificationType.MANAGER_ACTION_REQUIRED,
            related_request=request_obj,
        )

    return request_obj


@transaction.atomic
def cancel_request(actor, request_obj, reason="", http_request=None):
    if not user_can_cancel_request(actor, request_obj):
        raise PermissionDeniedError("Cannot cancel this request.")
    old_status = request_obj.status
    request_obj.status = RequestStatus.CANCELLED
    request_obj.cancelled_at = timezone.now()
    request_obj.current_approver = None
    request_obj.save(update_fields=["status", "cancelled_at", "current_approver", "updated_at"])
    _record_status_history(request_obj, actor, old_status, RequestStatus.CANCELLED, reason)
    audit_log(
        actor,
        AuditAction.REQUEST_CANCELLED,
        entity=request_obj,
        metadata={"reason": reason},
        request=http_request,
    )
    return request_obj


@transaction.atomic
def add_request_comment(actor, request_obj, body, is_internal=False, http_request=None):
    if not user_can_comment_on_request(actor, request_obj, is_internal=is_internal):
        raise PermissionDeniedError("Cannot comment on this request.")
    comment = RequestComment.objects.create(
        request=request_obj,
        author=actor,
        body=body,
        is_internal=is_internal,
    )
    create_notification(
        recipient=request_obj.requester,
        title=f"New comment on {request_obj.public_id}",
        message=f"{actor.full_name} commented on your request.",
        notification_type=NotificationType.REQUEST_COMMENTED,
        related_request=request_obj,
    )
    return comment


@transaction.atomic
def change_request_status(actor, request_obj, new_status, reason="", http_request=None):
    require_can_view_request(actor, request_obj)
    if new_status in FINAL_STATUSES and not (actor.is_admin_role or actor.is_ops):
        raise PermissionDeniedError("Cannot set final status.")
    old_status = request_obj.status
    request_obj.status = new_status
    if new_status == RequestStatus.FULFILLED:
        request_obj.resolved_at = timezone.now()
    request_obj.save(update_fields=["status", "resolved_at", "updated_at"])
    _record_status_history(request_obj, actor, old_status, new_status, reason)
    return request_obj

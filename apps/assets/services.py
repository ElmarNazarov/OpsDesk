from django.db import transaction
from django.utils import timezone

from apps.assets.models import AssetAssignment, AssetStatus
from apps.assets.permissions import user_can_assign_assets
from apps.audit.models import AuditAction
from apps.audit.services import audit_log
from apps.core.exceptions import InvalidStateError, PermissionDeniedError
from apps.notifications.models import NotificationType
from apps.notifications.services import create_notification
from apps.requests.models import RequestStatus
from apps.requests.services import change_request_status


@transaction.atomic
def assign_asset_to_employee(
    asset, employee, assigned_by, related_request=None, notes="", http_request=None
):
    if not user_can_assign_assets(assigned_by):
        raise PermissionDeniedError("Only Ops or Admin can assign assets.")
    if asset.status != AssetStatus.AVAILABLE:
        raise InvalidStateError("Asset is not available for assignment.")

    asset.status = AssetStatus.ASSIGNED
    asset.assigned_to = employee
    asset.save(update_fields=["status", "assigned_to", "updated_at"])

    assignment = AssetAssignment.objects.create(
        asset=asset,
        employee=employee,
        assigned_by=assigned_by,
        related_request=related_request,
        notes=notes,
    )
    audit_log(
        assigned_by,
        AuditAction.ASSET_ASSIGNED,
        entity=asset,
        metadata={"employee_id": employee.id, "assignment_id": assignment.id},
        request=http_request,
    )
    return assignment


@transaction.atomic
def return_asset(asset, returned_by, notes="", http_request=None):
    if not user_can_assign_assets(returned_by):
        raise PermissionDeniedError("Only Ops or Admin can return assets.")

    active = asset.assignments.filter(returned_at__isnull=True).order_by("-assigned_at").first()
    if active:
        active.returned_at = timezone.now()
        active.notes = notes or active.notes
        active.save(update_fields=["returned_at", "notes"])

    asset.status = AssetStatus.AVAILABLE
    asset.assigned_to = None
    asset.save(update_fields=["status", "assigned_to", "updated_at"])
    audit_log(returned_by, AuditAction.ASSET_RETURNED, entity=asset, request=http_request)
    return asset


@transaction.atomic
def fulfill_equipment_request(actor, request_obj, asset, http_request=None):
    if not user_can_assign_assets(actor):
        raise PermissionDeniedError("Only Ops or Admin can fulfill requests.")
    if request_obj.status not in (RequestStatus.APPROVED, RequestStatus.OPS_PROCESSING):
        raise InvalidStateError("Request must be approved before fulfillment.")

    assign_asset_to_employee(
        asset,
        request_obj.requester,
        actor,
        related_request=request_obj,
        http_request=http_request,
    )
    change_request_status(
        actor,
        request_obj,
        RequestStatus.FULFILLED,
        reason="Equipment fulfilled",
        http_request=http_request,
    )
    audit_log(actor, AuditAction.REQUEST_FULFILLED, entity=request_obj, request=http_request)
    create_notification(
        recipient=request_obj.requester,
        title=f"Request fulfilled: {request_obj.public_id}",
        message=f"Your equipment request has been fulfilled with {asset.name}.",
        notification_type=NotificationType.REQUEST_FULFILLED,
        related_request=request_obj,
    )
    return request_obj

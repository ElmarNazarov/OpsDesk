from celery import shared_task
from django.utils import timezone

from apps.core.utils import business_days_between
from apps.notifications.models import NotificationType
from apps.notifications.services import create_notification
from apps.requests.models import Request, RequestStatus


@shared_task
def mark_overdue_requests():
    now = timezone.now().date()
    qs = Request.objects.filter(
        status__in=[RequestStatus.SUBMITTED, RequestStatus.IN_REVIEW],
        submitted_at__isnull=False,
    ).select_related("current_approver")
    for request_obj in qs:
        submitted_date = request_obj.submitted_at.date()
        days = business_days_between(submitted_date, now)
        if days > 3 and not request_obj.metadata.get("overdue"):
            metadata = dict(request_obj.metadata)
            metadata["overdue"] = True
            request_obj.metadata = metadata
            request_obj.save(update_fields=["metadata", "updated_at"])
            if request_obj.current_approver:
                create_notification(
                    recipient=request_obj.current_approver,
                    title=f"Overdue request: {request_obj.public_id}",
                    message=f"Request '{request_obj.title}' has been pending for over 3 business days.",
                    notification_type=NotificationType.MANAGER_ACTION_REQUIRED,
                    related_request=request_obj,
                )

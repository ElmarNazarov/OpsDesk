from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import audit_log
from apps.notifications.models import Notification


def create_notification(
    recipient,
    title,
    message,
    notification_type,
    related_request=None,
):
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        type=notification_type,
        related_request=related_request,
    )
    audit_log(None, AuditAction.NOTIFICATION_CREATED, entity=notification)
    from apps.notifications.tasks import send_notification_email

    send_notification_email.delay(notification.id)
    return notification


def mark_notification_read(notification, user):
    if notification.recipient_id != user.id:
        from apps.core.exceptions import PermissionDeniedError

        raise PermissionDeniedError("Cannot mark another user's notification.")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
    return notification


def mark_all_notifications_read(user):
    return Notification.objects.filter(recipient=user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )

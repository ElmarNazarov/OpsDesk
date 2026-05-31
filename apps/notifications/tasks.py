from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.notifications.models import Notification


@shared_task
def send_notification_email(notification_id):
    try:
        notification = Notification.objects.select_related("recipient").get(pk=notification_id)
    except Notification.DoesNotExist:
        return
    send_mail(
        subject=notification.title,
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[notification.recipient.email],
        fail_silently=True,
    )


@shared_task
def cleanup_old_notifications():
    cutoff = timezone.now() - timedelta(days=90)
    Notification.objects.filter(created_at__lt=cutoff, is_read=True).delete()

from django.db.models import QuerySet

from apps.notifications.models import Notification


def get_notifications_for_user(user, limit=None) -> QuerySet[Notification]:
    qs = Notification.objects.filter(recipient=user).select_related("related_request")
    if limit:
        qs = qs[:limit]
    return qs


def get_unread_count(user) -> int:
    return Notification.objects.filter(recipient=user, is_read=False).count()


def get_recent_unread(user, limit=5) -> QuerySet[Notification]:
    return Notification.objects.filter(recipient=user, is_read=False).order_by("-created_at")[
        :limit
    ]

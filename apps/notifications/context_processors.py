from apps.notifications.selectors import get_recent_unread, get_unread_count


def notification_context(request):
    if not request.user.is_authenticated:
        return {"unread_notification_count": 0, "recent_notifications": []}
    return {
        "unread_notification_count": get_unread_count(request.user),
        "recent_notifications": list(get_recent_unread(request.user, limit=5)),
    }

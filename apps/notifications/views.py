from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.notifications.models import Notification
from apps.notifications.selectors import get_notifications_for_user
from apps.notifications.services import mark_all_notifications_read, mark_notification_read


@login_required
def notification_list(request):
    notifications = get_notifications_for_user(request.user)
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
def notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    mark_notification_read(notification, request.user)
    if notification.related_request_id:
        return redirect("requests:detail", public_id=notification.related_request.public_id)
    return redirect("notifications:list")


@login_required
def notification_mark_all_read(request):
    mark_all_notifications_read(request.user)
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications:list")

from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.approvals.selectors import get_pending_approvals_for_manager
from apps.assets.models import Asset, AssetStatus
from apps.assets.selectors import get_available_assets, get_fulfillment_queue
from apps.audit.models import AuditLog
from apps.notifications.selectors import get_notifications_for_user
from apps.requests.models import Request, RequestStatus
from apps.requests.selectors import get_open_requests_for_user, get_request_status_summary

User = get_user_model()


def get_employee_dashboard_context(user) -> dict:
    return {
        "open_requests": get_open_requests_for_user(user)[:10],
        "recent_notifications": get_notifications_for_user(user, limit=5),
        "status_summary": get_request_status_summary(user),
    }


def get_manager_dashboard_context(user) -> dict:
    from apps.approvals.selectors import get_approval_statistics, get_team_requests_for_manager

    return {
        "pending_approvals": get_pending_approvals_for_manager(user)[:10],
        "team_requests": get_team_requests_for_manager(user)[:10],
        "stats": get_approval_statistics(user),
    }


def get_ops_dashboard_context() -> dict:
    overdue = Request.objects.filter(
        metadata__overdue=True,
        status__in=[RequestStatus.SUBMITTED, RequestStatus.IN_REVIEW],
    ).count()
    return {
        "fulfillment_queue": get_fulfillment_queue()[:10],
        "available_assets": get_available_assets()[:10],
        "available_count": Asset.objects.filter(status=AssetStatus.AVAILABLE).count(),
        "overdue_count": overdue,
    }


def get_admin_dashboard_context() -> dict:
    return {
        "total_requests": Request.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "requests_by_category": list(
            Request.objects.values("category__name").annotate(count=Count("id")).order_by("-count")
        ),
        "requests_by_status": list(
            Request.objects.values("status").annotate(count=Count("id")).order_by("status")
        ),
        "recent_audit_logs": AuditLog.objects.select_related("actor")[:15],
    }

import json

from django.db.models import Count

from apps.approvals.models import ApprovalStep, ApprovalStepStatus
from apps.approvals.selectors import get_pending_approvals_for_manager
from apps.assets.selectors import get_assets_assigned_by_department
from apps.requests.models import Request


def get_requests_by_status_chart() -> str:
    data = list(Request.objects.values("status").annotate(count=Count("id")).order_by("status"))
    labels = [d["status"] for d in data]
    values = [d["count"] for d in data]
    return json.dumps({"labels": labels, "values": values})


def get_requests_by_category_chart() -> str:
    data = list(
        Request.objects.values("category__name").annotate(count=Count("id")).order_by("-count")
    )
    labels = [d["category__name"] for d in data]
    values = [d["count"] for d in data]
    return json.dumps({"labels": labels, "values": values})


def get_average_approval_time_days() -> float:
    steps = ApprovalStep.objects.filter(
        status=ApprovalStepStatus.APPROVED,
        decided_at__isnull=False,
    ).select_related("request")
    if not steps.exists():
        return 0.0
    total_days = 0
    count = 0
    for step in steps:
        if step.request.submitted_at and step.decided_at:
            delta = step.decided_at - step.request.submitted_at
            total_days += delta.total_seconds() / 86400
            count += 1
    return round(total_days / count, 1) if count else 0.0


def get_assets_by_department_chart() -> str:
    data = get_assets_assigned_by_department()
    return json.dumps(
        {"labels": [d["department"] for d in data], "values": [d["count"] for d in data]}
    )


def get_pending_approvals_by_manager() -> list[dict]:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    managers = User.objects.filter(groups__name="Manager", is_active=True)
    result = []
    for manager in managers:
        count = get_pending_approvals_for_manager(manager).count()
        if count:
            result.append({"manager": manager.full_name, "count": count})
    return result

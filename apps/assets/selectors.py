from django.db.models import Count, QuerySet

from apps.assets.models import Asset, AssetStatus
from apps.requests.models import Request, RequestStatus


def get_available_assets() -> QuerySet[Asset]:
    return Asset.objects.filter(status=AssetStatus.AVAILABLE).select_related("category", "location")


def get_assets_for_ops() -> QuerySet[Asset]:
    return Asset.objects.select_related("category", "location", "assigned_to")


def get_fulfillment_queue() -> QuerySet[Request]:
    return Request.objects.filter(
        status__in=[RequestStatus.APPROVED, RequestStatus.OPS_PROCESSING],
        category__slug__in=["equipment", "software-access"],
    ).select_related("category", "requester")


def get_assets_assigned_by_department() -> list[dict]:
    from apps.accounts.models import EmployeeProfile

    data = (
        EmployeeProfile.objects.filter(user__assigned_assets__isnull=False)
        .values("department__name")
        .annotate(count=Count("user__assigned_assets", distinct=True))
        .order_by("department__name")
    )
    return [
        {"department": d["department__name"] or "Unassigned", "count": d["count"]} for d in data
    ]

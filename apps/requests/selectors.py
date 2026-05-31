from django.db.models import Count, Q, QuerySet

from apps.accounts.permissions import user_can_manage_all, user_can_view_internal_comments
from apps.requests.models import Request, RequestCategory, RequestComment, RequestStatus


def generate_public_id() -> str:
    from django.utils import timezone

    year = timezone.now().year
    prefix = f"REQ-{year}-"
    last = (
        Request.objects.filter(public_id__startswith=prefix)
        .order_by("-public_id")
        .values_list("public_id", flat=True)
        .first()
    )
    seq = int(last.split("-")[-1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


def get_request_by_public_id(public_id: str) -> Request | None:
    return (
        Request.objects.select_related("category", "requester", "department", "current_approver")
        .filter(public_id=public_id)
        .first()
    )


def get_requests_for_user(user) -> QuerySet[Request]:
    qs = Request.objects.select_related("category", "requester", "department")
    if user_can_manage_all(user):
        return qs
    if user.is_manager or user.is_hr:
        profile = getattr(user, "profile", None)
        if profile and profile.department_id:
            return qs.filter(
                Q(requester=user)
                | Q(department_id=profile.department_id)
                | Q(requester__profile__manager=user)
            ).distinct()
    if user.is_ops:
        return qs.filter(
            status__in=[
                RequestStatus.APPROVED,
                RequestStatus.OPS_PROCESSING,
                RequestStatus.FULFILLED,
                RequestStatus.IN_REVIEW,
            ]
        )
    return qs.filter(requester=user)


def get_comments_for_request(user, request_obj: Request) -> QuerySet[RequestComment]:
    qs = request_obj.comments.select_related("author")
    if not user_can_view_internal_comments(user):
        qs = qs.filter(is_internal=False)
    return qs


def get_active_categories() -> QuerySet[RequestCategory]:
    return RequestCategory.objects.filter(is_active=True)


def get_open_requests_for_user(user) -> QuerySet[Request]:
    return get_requests_for_user(user).exclude(
        status__in=[RequestStatus.FULFILLED, RequestStatus.CANCELLED, RequestStatus.REJECTED]
    )


def get_request_status_summary(user) -> dict:
    qs = get_requests_for_user(user)
    counts = qs.values("status").annotate(count=Count("id"))
    return {item["status"]: item["count"] for item in counts}


def filter_requests(qs: QuerySet[Request], status=None, category=None, priority=None):
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    if priority:
        qs = qs.filter(priority=priority)
    return qs

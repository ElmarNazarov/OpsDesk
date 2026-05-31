from django.db.models import Q, QuerySet

from apps.requests.models import Request, RequestStatus


def get_pending_approvals_for_manager(user) -> QuerySet[Request]:
    if user.is_admin_role:
        return Request.objects.filter(
            status=RequestStatus.IN_REVIEW,
            current_approver__isnull=False,
        ).select_related("category", "requester", "current_approver")
    profile = getattr(user, "profile", None)
    if not profile:
        return Request.objects.none()
    return (
        Request.objects.filter(
            Q(current_approver=user)
            | Q(
                status=RequestStatus.IN_REVIEW,
                requester__profile__department_id=profile.department_id,
                requester__profile__manager=user,
            )
        )
        .select_related("category", "requester", "current_approver")
        .distinct()
    )


def get_team_requests_for_manager(user) -> QuerySet[Request]:
    profile = getattr(user, "profile", None)
    if user.is_admin_role:
        return Request.objects.select_related("category", "requester")
    if not profile or not profile.department_id:
        return Request.objects.none()
    return (
        Request.objects.filter(
            Q(requester__profile__department_id=profile.department_id)
            | Q(requester__profile__manager=user)
        )
        .select_related("category", "requester")
        .distinct()
    )


def get_approval_statistics(user) -> dict:
    pending = get_pending_approvals_for_manager(user).count()
    team = get_team_requests_for_manager(user)
    approved = team.filter(status=RequestStatus.APPROVED).count()
    rejected = team.filter(status=RequestStatus.REJECTED).count()
    return {"pending": pending, "approved": approved, "rejected": rejected}

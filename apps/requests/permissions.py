from django.core.exceptions import PermissionDenied

from apps.accounts.permissions import user_can_manage_all, user_can_view_internal_comments
from apps.requests.models import Request, RequestStatus


def user_can_view_request(user, request_obj: Request) -> bool:
    if not user.is_authenticated:
        return False
    if user_can_manage_all(user):
        return True
    if request_obj.requester_id == user.id:
        return True
    if user.is_manager or user.is_hr:
        profile = getattr(user, "profile", None)
        if profile and profile.department_id:
            if request_obj.department_id == profile.department_id:
                return True
            if request_obj.requester.profile.manager_id == user.id:
                return True
            team = getattr(request_obj.requester.profile, "team", None)
            if team and team.lead_id == user.id:
                return True
    if user.is_ops:
        return request_obj.status in (
            RequestStatus.APPROVED,
            RequestStatus.OPS_PROCESSING,
            RequestStatus.FULFILLED,
        )
    return False


def user_can_edit_request(user, request_obj: Request) -> bool:
    if not user.is_authenticated:
        return False
    if request_obj.status != RequestStatus.DRAFT:
        return False
    if user_can_manage_all(user):
        return True
    return request_obj.requester_id == user.id


def user_can_submit_request(user, request_obj: Request) -> bool:
    if request_obj.status != RequestStatus.DRAFT:
        return False
    if user_can_manage_all(user):
        return True
    return request_obj.requester_id == user.id


def user_can_cancel_request(user, request_obj: Request) -> bool:
    if request_obj.status in (
        RequestStatus.REJECTED,
        RequestStatus.FULFILLED,
        RequestStatus.CANCELLED,
    ):
        return False
    if user_can_manage_all(user):
        return True
    if request_obj.requester_id != user.id:
        return False
    return request_obj.status in (
        RequestStatus.DRAFT,
        RequestStatus.SUBMITTED,
        RequestStatus.IN_REVIEW,
    )


def user_can_comment_on_request(user, request_obj: Request, is_internal: bool = False) -> bool:
    if not user_can_view_request(user, request_obj):
        return False
    return not is_internal or user_can_view_internal_comments(user)


def require_can_view_request(user, request_obj: Request):
    if not user_can_view_request(user, request_obj):
        raise PermissionDenied("You cannot view this request.")

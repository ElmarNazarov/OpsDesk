from apps.accounts.permissions import user_can_manage_all
from apps.approvals.models import ApprovalStepStatus, RoleRequired
from apps.requests.models import Request


def _get_approval_flags(request_obj: Request):
    policy = getattr(request_obj.category, "approval_policy", None)
    if policy and policy.is_active:
        return (
            policy.requires_manager_approval,
            policy.requires_ops_approval,
            policy.requires_hr_approval,
        )
    cat = request_obj.category
    return (
        cat.requires_manager_approval,
        cat.requires_ops_approval,
        cat.requires_hr_approval,
    )


def user_can_approve_request(user, request_obj: Request) -> bool:
    if not user.is_authenticated:
        return False
    if request_obj.requester_id == user.id:
        return False
    if user_can_manage_all(user):
        return True

    current_step = (
        request_obj.approval_steps.filter(status=ApprovalStepStatus.PENDING)
        .order_by("step_order")
        .first()
    )
    if not current_step:
        return False

    if current_step.approver_id == user.id:
        return True

    if current_step.role_required == RoleRequired.MANAGER and user.is_manager:
        return _manager_can_approve_team(user, request_obj)
    if current_step.role_required == RoleRequired.HR and user.is_hr:
        return True
    return current_step.role_required == RoleRequired.OPS and user.is_ops


def _manager_can_approve_team(user, request_obj: Request) -> bool:
    profile = getattr(user, "profile", None)
    if not profile or not profile.department_id:
        return False
    requester_profile = getattr(request_obj.requester, "profile", None)
    if not requester_profile:
        return False
    if requester_profile.department_id != profile.department_id:
        return False
    if requester_profile.manager_id == user.id:
        return True
    if request_obj.department_id == profile.department_id:
        return True
    team = requester_profile.team
    return bool(team and team.lead_id == user.id)


def user_can_reject_request(user, request_obj: Request) -> bool:
    return user_can_approve_request(user, request_obj)

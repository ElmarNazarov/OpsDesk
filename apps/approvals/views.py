from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.approvals.selectors import (
    get_approval_statistics,
    get_pending_approvals_for_manager,
    get_team_requests_for_manager,
)


@login_required
def manager_dashboard(request):
    if not (request.user.is_manager or request.user.is_admin_role or request.user.is_hr):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    return render(
        request,
        "manager/dashboard.html",
        {
            "pending_approvals": get_pending_approvals_for_manager(request.user),
            "team_requests": get_team_requests_for_manager(request.user)[:10],
            "stats": get_approval_statistics(request.user),
        },
    )


@login_required
def manager_approvals(request):
    if not (request.user.is_manager or request.user.is_admin_role or request.user.is_hr):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    return render(
        request,
        "manager/approvals.html",
        {"pending_approvals": get_pending_approvals_for_manager(request.user)},
    )


@login_required
def manager_requests(request):
    if not (request.user.is_manager or request.user.is_admin_role or request.user.is_hr):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    return render(
        request,
        "manager/requests.html",
        {"team_requests": get_team_requests_for_manager(request.user)},
    )

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.dashboard.selectors import (
    get_admin_dashboard_context,
    get_employee_dashboard_context,
    get_manager_dashboard_context,
    get_ops_dashboard_context,
)


@login_required
def employee_dashboard(request):
    ctx = get_employee_dashboard_context(request.user)
    return render(request, "dashboard/employee.html", ctx)


@login_required
def manager_dashboard_redirect(request):
    if not (request.user.is_manager or request.user.is_admin_role or request.user.is_hr):
        raise PermissionDenied
    ctx = get_manager_dashboard_context(request.user)
    return render(request, "manager/dashboard.html", ctx)


@login_required
def ops_dashboard_view(request):
    if not (request.user.is_ops or request.user.is_admin_role):
        raise PermissionDenied
    ctx = get_ops_dashboard_context()
    return render(request, "ops/dashboard.html", ctx)


@login_required
def admin_dashboard(request):
    if not (request.user.is_admin_role or request.user.is_superuser):
        raise PermissionDenied
    ctx = get_admin_dashboard_context()
    return render(request, "dashboard/admin.html", ctx)

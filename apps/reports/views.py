from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.reports.selectors import (
    get_assets_by_department_chart,
    get_average_approval_time_days,
    get_pending_approvals_by_manager,
    get_requests_by_category_chart,
    get_requests_by_status_chart,
)


@login_required
def reports_index(request):
    return render(request, "reports/index.html")


@login_required
def reports_requests(request):
    return render(
        request,
        "reports/requests.html",
        {
            "status_chart": get_requests_by_status_chart(),
            "category_chart": get_requests_by_category_chart(),
            "avg_approval_days": get_average_approval_time_days(),
            "pending_by_manager": get_pending_approvals_by_manager(),
        },
    )


@login_required
def reports_assets(request):
    return render(
        request,
        "reports/assets.html",
        {"department_chart": get_assets_by_department_chart()},
    )

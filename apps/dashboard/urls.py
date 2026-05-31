from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", views.employee_dashboard, name="employee"),
    path("manager/dashboard/", views.manager_dashboard_redirect, name="manager"),
    path("ops/dashboard/", views.ops_dashboard_view, name="ops"),
    path("admin-dashboard/", views.admin_dashboard, name="admin"),
    path("", views.employee_dashboard, name="home"),
]

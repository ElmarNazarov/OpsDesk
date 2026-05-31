from django.urls import path

from apps.reports import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("requests/", views.reports_requests, name="requests"),
    path("assets/", views.reports_assets, name="assets"),
]

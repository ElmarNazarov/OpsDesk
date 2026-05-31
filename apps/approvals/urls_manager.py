from django.urls import path

from apps.approvals import views as approval_views

app_name = "manager"

urlpatterns = [
    path("approvals/", approval_views.manager_approvals, name="approvals"),
    path("requests/", approval_views.manager_requests, name="requests"),
]

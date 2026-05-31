from django.urls import path

from apps.requests import views

app_name = "requests"

urlpatterns = [
    path("", views.request_list, name="list"),
    path("new/", views.request_create, name="create"),
    path("<str:public_id>/", views.request_detail, name="detail"),
    path("<str:public_id>/edit/", views.request_edit, name="edit"),
    path("<str:public_id>/submit/", views.request_submit, name="submit"),
    path("<str:public_id>/cancel/", views.request_cancel, name="cancel"),
    path("<str:public_id>/comment/", views.request_comment, name="comment"),
    path("<str:public_id>/approve/", views.request_approve, name="approve"),
    path("<str:public_id>/reject/", views.request_reject, name="reject"),
]

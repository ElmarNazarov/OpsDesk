from django.urls import path

from apps.accounts.views import OpsDeskLoginView, logout_view, profile_view

app_name = "accounts"

urlpatterns = [
    path("login/", OpsDeskLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]

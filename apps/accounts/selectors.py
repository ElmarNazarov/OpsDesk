from django.urls import reverse


def get_dashboard_redirect_url(user) -> str:
    if user.is_admin_role or user.is_superuser:
        return reverse("dashboard:admin")
    if user.is_ops:
        return reverse("dashboard:ops")
    if user.is_manager:
        return reverse("dashboard:manager")
    return reverse("dashboard:employee")

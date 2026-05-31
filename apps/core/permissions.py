from django.core.exceptions import PermissionDenied


def user_in_group(user, group_name: str) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


class RoleRequiredMixin:
    """Mixin requiring user to be in at least one of required_groups."""

    required_groups: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_groups and not any(
            user_in_group(request.user, g) for g in self.required_groups
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

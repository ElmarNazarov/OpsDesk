def user_can_manage_all(user) -> bool:
    return user.is_authenticated and (user.is_admin_role or user.is_superuser)


def user_is_manager_or_above(user) -> bool:
    return user.is_authenticated and (
        user.is_admin_role or user.is_manager or user.is_hr or user.is_ops
    )


def user_can_view_internal_comments(user) -> bool:
    return user.is_authenticated and (
        user.is_admin_role or user.is_manager or user.is_ops or user.is_hr
    )

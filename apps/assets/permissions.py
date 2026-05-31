def user_can_assign_assets(user) -> bool:
    return user.is_authenticated and (user.is_ops or user.is_admin_role)


def user_can_manage_assets(user) -> bool:
    return user_can_assign_assets(user)

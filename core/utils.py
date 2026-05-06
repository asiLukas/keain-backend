from strawberry import Info


def get_user_from_info(info: Info):
    return info.context.get("user")

import strawberry
import strawberry_django

from user.models import KeainUser


@strawberry_django.type(KeainUser)
class KeainUserType:
    id: strawberry.auto
    username: strawberry.auto
    email: strawberry.auto
    is_active: strawberry.auto
    theme: KeainUser.AppTheme

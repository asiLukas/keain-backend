import strawberry
import strawberry_django

from .types import KeainUserType


@strawberry.type
class KeainUserQuery:
    users: list[KeainUserType] = strawberry_django.field()
    user: KeainUserType = strawberry_django.field()

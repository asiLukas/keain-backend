import strawberry
import strawberry_django
from strawberry.types.info import Info

from .types import KeainUserType


@strawberry.type
class KeainUserQuery:
    users: list[KeainUserType] = strawberry_django.field()
    user: KeainUserType = strawberry_django.field()

    @strawberry.field
    def me(self, info: Info) -> KeainUserType:
        user = info.context.get("user")
        if user is None:
            raise ValueError("Not authenticated")
        return user

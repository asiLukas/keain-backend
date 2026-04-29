import strawberry
from graphql import GraphQLError
from strawberry.types.info import Info

from core.permissions import IsAuthenticated, IsSuperuser
from user.models import KeainUser

from .types import KeainUserType


@strawberry.type
class KeainUserQuery:
    @strawberry.field(permission_classes=[IsSuperuser])
    def users(self, info: Info) -> list[KeainUserType]:
        return KeainUser.objects.all()

    @strawberry.field(permission_classes=[IsSuperuser])
    def user(self, info: Info, id: strawberry.ID) -> KeainUserType:
        try:
            return KeainUser.objects.get(pk=id)
        except KeainUser.DoesNotExist:
            raise GraphQLError("User not found.", extensions={"code": 404})

    @strawberry.field(permission_classes=[IsAuthenticated])
    def me(self, info: Info) -> KeainUserType:
        return info.context["user"]

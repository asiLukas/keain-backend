from graphql import GraphQLError
from strawberry.permission import BasePermission
from strawberry.types import Info

from core.error_codes import FORBIDDEN, UNAUTHENTICATED, err


class IsAuthenticated(BasePermission):
    message = "Not authenticated."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        return info.context.get("user") is not None

    def on_unauthorized(self):
        raise GraphQLError(self.message, extensions=err(UNAUTHENTICATED))


class IsSuperuser(BasePermission):
    message = "Forbidden."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user = info.context.get("user")
        return user is not None and user.is_superuser

    def on_unauthorized(self):
        raise GraphQLError(self.message, extensions=err(FORBIDDEN))

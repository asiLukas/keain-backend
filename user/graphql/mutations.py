import jwt
import strawberry
from django.db import IntegrityError
from graphql import GraphQLError
from strawberry.types.info import Info

from core.permissions import IsAuthenticated
from user.graphql.types import AuthType, KeainUserType
from user.models import KeainUser
from user.tokens import create_access_token, create_refresh_token, decode_token


@strawberry.type
class KeainUserMutation:
    @strawberry.mutation(description="Create a new user")
    def create_user(self, username: str, email: str, password: str) -> KeainUserType:
        try:
            user = KeainUser.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            raise GraphQLError("Username already taken.", extensions={"code": 409})
        return user

    @strawberry.mutation(description="Update a user's theme", permission_classes=[IsAuthenticated])
    def update_user_theme(self, info: Info, theme: KeainUser.AppTheme) -> KeainUserType:
        user = info.context["user"]
        user.theme = theme
        user.save()
        return user

    @strawberry.mutation(description="Authenticate a user and return an auth payload")
    def login(self, username: str, password: str) -> AuthType:
        try:
            user = KeainUser.objects.get(username=username)
        except KeainUser.DoesNotExist:
            raise GraphQLError("Invalid credentials.", extensions={"code": 401})
        if not user.check_password(password):
            raise GraphQLError("Invalid credentials.", extensions={"code": 401})

        return AuthType(
            access_token=create_access_token(user.username),
            refresh_token=create_refresh_token(user.username),
            user=user,
        )

    @strawberry.mutation(description="Refresh an access token")
    def refresh_token(self, refresh_token: str) -> AuthType:
        try:
            payload = decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise GraphQLError("Refresh token has expired", extensions={"code": 401})
        except jwt.InvalidTokenError:
            raise GraphQLError("Invalid refresh token", extensions={"code": 401})

        if payload.get("type") != "refresh":
            raise GraphQLError("Invalid token type", extensions={"code": 401})

        try:
            user = KeainUser.objects.get(username=payload["sub"])
        except KeainUser.DoesNotExist:
            raise GraphQLError("Invalid token", extensions={"code": 401})
        return AuthType(
            access_token=create_access_token(user.username),
            refresh_token=create_refresh_token(user.username),
            user=user,
        )

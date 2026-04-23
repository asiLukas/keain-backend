import jwt
import strawberry
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from user.graphql.types import KeainUserType
from user.models import KeainUser
from user.tokens import create_access_token, create_refresh_token, decode_token


@strawberry.type
class AuthType:
    access_token: str
    refresh_token: str
    user: KeainUserType


@strawberry.type
class RefreshType:
    access_token: str


@strawberry.type
class KeainUserMutation:
    @strawberry.mutation(description="Create a new user")
    def create_user(self, username: str, email: str, password: str) -> KeainUserType:
        try:
            user = KeainUser.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            raise ValueError("Username already exists")
        return user

    @strawberry.mutation(description="Update a user's theme")
    def update_user_theme(self, username: str, theme: KeainUser.AppTheme) -> KeainUserType:
        user = get_object_or_404(KeainUser, username=username)
        user.theme = theme
        user.save()
        return user

    @strawberry.mutation(description="Authenticate a user and return an auth payload")
    def login(self, username: str, password: str) -> AuthType:
        user = get_object_or_404(KeainUser, username=username)
        if not user.check_password(password):
            raise ValueError("Invalid credentials")

        return AuthType(
            access_token=create_access_token(user.username),
            refresh_token=create_refresh_token(user.username),
            user=user,
        )

    @strawberry.mutation(description="Refresh an access token")
    def refresh_token(self, refresh_token: str) -> RefreshType:
        try:
            payload = decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user = get_object_or_404(KeainUser, username=payload["sub"])
        return RefreshType(access_token=create_access_token(user.username))

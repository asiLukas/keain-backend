from typing import Optional

import jwt
import strawberry
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from graphql import GraphQLError
from strawberry.types.info import Info

from analyzer.models import MetricChoice
from core.error_codes import CONFLICT, UNAUTHENTICATED, err
from core.permissions import IsAuthenticated
from user.graphql.types import AuthType, KeainUserType
from user.models import KeainUser
from user.tokens import create_access_token, create_refresh_token, decode_token

_DUMMY_PASSWORD_HASH = make_password("dummy-password-for-constant-time-login")


@strawberry.type
class KeainUserMutation:
    @strawberry.mutation(description="Create a new user")
    def create_user(self, username: str, email: str, password: str) -> KeainUserType:
        try:
            user = KeainUser.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            raise GraphQLError("Username already taken.", extensions=err(CONFLICT))
        return user

    @strawberry.mutation(description="Update a user's theme", permission_classes=[IsAuthenticated])
    def update_user_theme(self, info: Info, theme: KeainUser.AppTheme) -> KeainUserType:
        user = info.context["user"]
        user.theme = theme
        user.save()
        return user

    @strawberry.mutation(
        description="Update a user's metrics", permission_classes=[IsAuthenticated]
    )
    def update_user_metrics(
        self,
        info: Info,
        primary_metric: Optional[MetricChoice] = None,
        secondary_metric: Optional[MetricChoice] = None,
    ) -> KeainUserType:
        user = info.context["user"]
        if primary_metric:
            user.primary_metric = primary_metric
        if secondary_metric:
            user.secondary_metric = secondary_metric
        user.save()
        return user

    @strawberry.mutation(description="Authenticate a user and return an auth payload")
    def login(self, username: str, password: str) -> AuthType:
        user = KeainUser.objects.filter(username=username).first()
        pw_hash = user.password if user else _DUMMY_PASSWORD_HASH
        pw_ok = check_password(password, pw_hash)
        if user is None or not pw_ok:
            raise GraphQLError("Invalid credentials.", extensions=err(UNAUTHENTICATED))

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
            raise GraphQLError("Refresh token has expired", extensions=err(UNAUTHENTICATED))
        except jwt.InvalidTokenError:
            raise GraphQLError("Invalid refresh token", extensions=err(UNAUTHENTICATED))

        if payload.get("type") != "refresh":
            raise GraphQLError("Invalid token type", extensions=err(UNAUTHENTICATED))

        try:
            user = KeainUser.objects.get(username=payload["sub"])
        except KeainUser.DoesNotExist:
            raise GraphQLError("Invalid token", extensions=err(UNAUTHENTICATED))
        return AuthType(
            access_token=create_access_token(user.username),
            refresh_token=create_refresh_token(user.username),
            user=user,
        )

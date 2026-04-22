import strawberry
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from user.graphql.types import KeainUserType
from user.models import KeainUser


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

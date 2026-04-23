from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone


def create_access_token(username: int) -> str:
    payload = {
        "sub": username,
        "exp": timezone.now() + timedelta(minutes=15),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(username: int) -> str:
    payload = {
        "sub": username,
        "exp": timezone.now() + timedelta(days=30),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

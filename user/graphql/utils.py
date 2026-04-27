from typing import Optional

import jwt

from user.models import KeainUser
from user.tokens import decode_token


def get_user_from_request(request) -> Optional[KeainUser]:
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ")
    try:
        payload = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    if payload.get("type") != "access":
        return None
    return KeainUser.objects.filter(username=payload["sub"]).first()

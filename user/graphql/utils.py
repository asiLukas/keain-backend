from functools import wraps
from typing import Optional

import jwt
from django.core.cache import cache
from graphql import GraphQLError
from strawberry import Info

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


def rate_limit(action: str, max_requests: int, window_seconds: int):
    """
    Limits the number of times a resolver can be called by a specific IP.
    """

    def decorator(resolver_func):
        @wraps(resolver_func)
        def wrapper(self, info: Info, *args, **kwargs):
            request = info.context["request"]

            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")

            cache_key = f"ratelimit:{action}:{ip}"

            requests = cache.get(cache_key, 0)
            if requests >= max_requests:
                raise GraphQLError(
                    "Rate limit exceeded. Please try again later.",
                    extensions={"code": "TOO_MANY_REQUESTS", "http_status": 429},
                )

            if requests == 0:
                cache.set(cache_key, 1, timeout=window_seconds)
            else:
                try:
                    cache.incr(cache_key)
                except ValueError:
                    cache.set(cache_key, 1, timeout=window_seconds)

            return resolver_func(self, info, *args, **kwargs)

        return wrapper

    return decorator

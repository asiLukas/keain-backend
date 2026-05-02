from functools import wraps
from typing import Optional

import jwt
from django.conf import settings
from django.core.cache import cache
from graphql import GraphQLError
from strawberry import Info

from core.error_codes import TOO_MANY_REQUESTS, err
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


def _client_ip(request) -> str:
    """Return the client IP, only honoring X-Forwarded-For when configured.

    `TRUST_PROXY_HEADERS` should be True only when Django sits behind a known
    reverse proxy (nginx, Cloudflare, ALB, etc.) that overwrites or appends
    X-Forwarded-For. The proxy must be configured to *replace* any client-
    supplied XFF header, otherwise rate limits can be bypassed by spoofing.

    When trusted, we take the rightmost hop (the proxy's appended client IP).
    Anything to the left is attacker-controlled.
    """
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            parts = [p.strip() for p in xff.split(",") if p.strip()]
            if parts:
                return parts[-1]
    return request.META.get("REMOTE_ADDR") or "unknown"


def rate_limit(action: str, max_requests: int, window_seconds: int):
    """
    Limits the number of times a resolver can be called by a specific IP.
    """

    def decorator(resolver_func):
        @wraps(resolver_func)
        def wrapper(self, info: Info, *args, **kwargs):
            request = info.context["request"]
            ip = _client_ip(request)
            cache_key = f"ratelimit:{action}:{ip}"

            requests = cache.get(cache_key, 0)
            if requests >= max_requests:
                raise GraphQLError(
                    "Rate limit exceeded. Please try again later.",
                    extensions=err(TOO_MANY_REQUESTS),
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

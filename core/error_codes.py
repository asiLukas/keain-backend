"""Standardized GraphQL error codes.

Every GraphQLError raised in the project should pass `extensions=err(CODE, ...)`
so clients can branch on a single, stable string. The numeric `status` mirrors
the closest HTTP status for transports that want to surface it.
"""

from typing import Any

UNAUTHENTICATED = "UNAUTHENTICATED"  # 401
FORBIDDEN = "FORBIDDEN"  # 403
NOT_FOUND = "NOT_FOUND"  # 404
CONFLICT = "CONFLICT"  # 409
INVALID_INPUT = "INVALID_INPUT"  # 400
INVALID_AUDIO = "INVALID_AUDIO"  # 400 (specialized; analyzer rejects)
TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"  # 429
INTERNAL = "INTERNAL"  # 500

_STATUS: dict[str, int] = {
    UNAUTHENTICATED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    INVALID_INPUT: 400,
    INVALID_AUDIO: 400,
    TOO_MANY_REQUESTS: 429,
    INTERNAL: 500,
}


def err(code: str, **extra: Any) -> dict[str, Any]:
    """Build the `extensions` dict for a GraphQLError."""
    return {"code": code, "status": _STATUS[code], **extra}

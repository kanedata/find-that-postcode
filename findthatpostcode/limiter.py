import os

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

RATE_LIMIT_EXEMPT_HEADER = "X-RateLimit-Exempt"
RATE_LIMIT_EXEMPT_KEYS = os.environ.get("RATE_LIMIT_EXEMPT_KEYS", "").split(",")


def exempt_if_header():
    if request.headers.get(RATE_LIMIT_EXEMPT_HEADER) in RATE_LIMIT_EXEMPT_KEYS:
        return True
    return False


limiter = Limiter(
    get_remote_address,
    default_limits=["2 per second"],
    application_limits=["20000 per day"],
    storage_uri="memory://",
    headers_enabled=True,
    default_limits_exempt_when=exempt_if_header,
    application_limits_exempt_when=exempt_if_header,
)

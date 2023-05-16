from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

# "10/second "
limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])


def apply_limiter_to_application(application: FastAPI) -> None:
    application.state.limiter = limiter
    application.add_exception_handler(
        RateLimitExceeded, _rate_limit_exceeded_handler
    )
    application.add_middleware(SlowAPIMiddleware)

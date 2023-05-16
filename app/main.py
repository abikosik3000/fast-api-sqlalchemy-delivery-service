from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import couriers_router, other_router, orders_router
from app.limiter import apply_limiter_to_application
from app.database import start_migration


@asynccontextmanager
async def lifespan(application: FastAPI):
    start_migration()
    yield


def get_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    apply_limiter_to_application(application)

    application.include_router(other_router.router)
    application.include_router(couriers_router.router)
    application.include_router(orders_router.router)
    return application


app = get_application()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )

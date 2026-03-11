from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi_identity.api.roues.v1.auth_routes import create_auth_router
from fastapi_identity.core.database import init_db, close_db, check_db_ready
from fastapi_identity.core.exception_handlers import register_exception_handlers
from fastapi_identity.core.logging import get_logger, setup_logging
from fastapi_identity.core.settings import get_settings
from fastapi_identity.services.token_service import TokenService

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app_in: FastAPI):
    setup_logging()
    logger.info("Application starting")

    await init_db()
    logger.info("Database initialized")
    yield

    logger.info("Application shutting down")
    await close_db()


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_exception_handlers(application)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials and settings.cors_origins.strip() != "*",
        allow_methods=settings.cors_allow_methods.split(","),
        allow_headers=settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"],
    )

    # --- Wire up identity ---
    token_service = TokenService()

    auth_router = create_auth_router(token_service=token_service)
    application.include_router(auth_router)

    return application


app = create_application()


@app.get("/")
def root():
    logger.debug("Root endpoint requested")
    return {"message": "FastAPI Identity Server"}


@app.get("/health")
def health_check():
    logger.debug("Health check requested")
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_probe():
    """Readiness probe: returns 200 if dependencies (e.g. DB) are reachable, else 503."""
    logger.debug("Readiness probe requested")
    if await check_db_ready():
        return {"status": "ready"}
    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "detail": "database unreachable"},
    )

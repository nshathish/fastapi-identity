import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse

from fastapi_identity.core.logging import get_logger
from fastapi_identity.core.problem_details import ERROR_TYPES, create_problem_response
from fastapi_identity.core.settings import get_settings

logger = get_logger("exception_handlers")
settings = get_settings()


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    type_uri = ERROR_TYPES.get(
        {
            400: "bad_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
        }.get(exc.status_code),
        f"https://httpstatuses.com/{exc.status_code}"
    )

    title = exc.detail.split(":")[0].strip() if ":" in exc.detail else exc.detail
    title = title.capitalize()

    body = create_problem_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        type_uri=type_uri,
        instance=request.url.path,
        request_id=request_id,
    )

    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    errors = [
        {
            "field": ".".join(str(loc) for loc in error["loc"] if loc != "body"),
            "message": error["msg"],
            "code": error.get("type"),
        }
        for error in exc.errors()
    ]

    body = create_problem_response(
        status_code=422,
        title="Validation Failed",
        detail="The request contains invalid parameters.",
        type_uri=ERROR_TYPES["validation"],
        instance=request.url.path,
        request_id=request_id,
        errors=errors,
    )

    return JSONResponse(status_code=422, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception("Unhandled exception: %s", exc, exc_info=True)

    if settings.debug:
        detail = str(exc)
        title = type(exc).__name__
        error_code = type(exc).__name__
    else:
        detail = "An unexpected error occurred. Please contact support."
        title = "Internal Server Error"
        error_code = "INTERNAL_ERROR"

    body = create_problem_response(
        status_code=500,
        title=title,
        detail=detail,
        type_uri=ERROR_TYPES["internal"],
        instance=request.url.path,
        request_id=request_id,
        error_code=error_code,  # Custom extension field
    )

    return JSONResponse(status_code=500, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers and request-id middleware on the fastapi_template_project."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

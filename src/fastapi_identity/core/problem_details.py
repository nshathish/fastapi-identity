from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ProblemError(BaseModel):
    field: str
    message: str
    code: str | None


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details response schema."""
    type: str = Field(
        default="https://httpstatuses.com/500",
        description="URI identifying the error type"
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary"
    )
    status: int = Field(
        ...,
        ge=100,
        le=599,
        description="HTTP status code"
    )
    detail: str = Field(
        ...,
        description="Human-readable explanation specific to this occurrence"
    )
    instance: str | None = Field(
        default=None,
        description="URI identifying the specific resource"
    )
    request_id: str | None = Field(
        default=None,
        description="Request ID for tracing"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the error occurred"
    )
    errors: list[ProblemError] | None = Field(
        default=None,
        description="Field-level validation errors"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "https://httpstatuses.com/404",
                "title": "Not Found",
                "status": 404,
                "detail": "The requested resource was not found",
                "instance": "/api/items/123",
                "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "timestamp": "2024-01-15T10:30:45.123456+00:00"
            }
        }


# Error type URIs for documentation
ERROR_TYPES = {
    "validation": "https://api.example.com/errors/validation",
    "not_found": "https://api.example.com/errors/not-found",
    "unauthorized": "https://api.example.com/errors/unauthorized",
    "forbidden": "https://api.example.com/errors/forbidden",
    "bad_request": "https://api.example.com/errors/bad-request",
    "internal": "https://api.example.com/errors/internal",
    "conflict": "https://api.example.com/errors/conflict",
}


def create_problem_response(
        status_code: int,
        title: str,
        detail: str,
        type_uri: str | None = None,
        instance: str | None = None,
        request_id: str | None = None,
        errors: list[dict] | None = None,
        **extensions: Any
) -> dict:
    """
    Build an RFC 7807 Problem Details response dictionary.

    Args:
        status_code: HTTP status code (400, 404, 500, etc.)
        title: Short, human-readable summary
        detail: Specific explanation for this occurrence
        type_uri: URI identifying error type (auto-generated if not provided)
        instance: URI of the specific resource that had the error
        request_id: Request ID for tracing
        errors: List of field-level validation errors
        **extensions: Any additional RFC 7807 extension fields

    Returns:
        dict ready for JSONResponse
    """
    if not type_uri:
        type_uri = f"https://httpstatuses.com/{status_code}"

    body = {
        "type": type_uri,
        "title": title,
        "status": status_code,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if instance:
        body["instance"] = instance
    if request_id:
        body["request_id"] = request_id
    if errors:
        body["errors"] = errors

    # Add any custom extension fields
    body.update({k: v for k, v in extensions.items() if v is not None})

    return body

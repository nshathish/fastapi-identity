from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_name: str = Field(
        default="FastAPI Identity Server",
        min_length=1,
        description="Application name.",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode.",
    )
    database_url: str = Field(
        default="postgresql://fastapi_user:fastapi_password!123@localhost:5432/fastapi_identity_db",
        min_length=1,
        description="PostgreSQL connection URL (postgresql:// or postgresql+asyncpg://).",
    )

    # JWT
    secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION",
        min_length=8,
        description="Secret key for signing JWT tokens.",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm.",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        description="Access token lifetime in minutes.",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        gt=0,
        description="Refresh token lifetime in days.",
    )
    issuer: str = Field(
        default="fastapi-identity",
        min_length=1,
        description="JWT issuer claim.",
    )
    audience: str = Field(
        default="fastapi-identity-client",
        min_length=1,
        description="JWT audience claim.",
    )

    # CORS
    cors_origins: str = Field(
        default="*",
        min_length=1,
        description="Comma-separated allowed origins or * for all.",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests.",
    )
    cors_allow_methods: str = Field(
        default="GET,POST,PUT,PATCH,DELETE,OPTIONS",
        min_length=1,
        description="Comma-separated allowed HTTP methods.",
    )
    cors_allow_headers: str = Field(
        default="*",
        min_length=1,
        description="Comma-separated allowed headers or * for all.",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("database_url must not be empty")
        lower = v.strip().lower()
        if not (
                lower.startswith("postgresql://")
                or lower.startswith("postgresql+asyncpg://")
        ):
            raise ValueError(
                "database_url must start with postgresql:// or postgresql+asyncpg://"
            )
        return v.strip()

    @field_validator("app_name", "cors_origins", "cors_allow_methods", "cors_allow_headers")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        """URL for async engine (postgresql+asyncpg)."""
        url = self.database_url
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

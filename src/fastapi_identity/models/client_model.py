import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class OAuthClient(SQLModel, table=True):
    """A registered OAuth2 client application."""

    __tablename__ = "identity_oauth_clients"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    client_id: str = Field(unique=True, index=True)
    client_secret: str | None = Field(default=None)
    client_name: str
    redirect_uris: str = Field(
        description="Comma-separated list of allowed redirect URIs.",
    )
    allowed_scopes: str = Field(
        default="openid profile email",
        description="Space-separated list of allowed scopes.",
    )
    is_active: bool = Field(default=True)
    is_public: bool = Field(
        default=True,
        description="Public clients (SPAs, mobile) don't have a client_secret.",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def redirect_uris_list(self) -> list[str]:
        return [u.strip() for u in self.redirect_uris.split(",") if u.strip()]

    @property
    def allowed_scopes_list(self) -> list[str]:
        return [s.strip() for s in self.allowed_scopes.split(" ") if s.strip()]

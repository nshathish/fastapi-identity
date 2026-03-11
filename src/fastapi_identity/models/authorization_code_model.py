import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class AuthorizationCode(SQLModel, table=True):
    """A short-lived authorization code issued during the authorize step."""

    __tablename__ = "identity_authorization_codes"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    code: str = Field(unique=True, index=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    redirect_uri: str
    scopes: str = Field(default="")
    code_challenge: str | None = Field(default=None)
    code_challenge_method: str | None = Field(default=None)
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

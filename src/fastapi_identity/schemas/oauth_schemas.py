from pydantic import BaseModel, Field


class AuthorizeRequest(BaseModel):
    """Query parameters for GET /authorize."""

    response_type: str = Field(description="Must be 'code'.")
    client_id: str
    redirect_uri: str
    scope: str = Field(default="openid")
    state: str | None = Field(default=None)
    code_challenge: str | None = Field(default=None)
    code_challenge_method: str | None = Field(default=None)


class AuthorizeLoginRequest(BaseModel):
    """User submits credentials on the login form during /authorize."""

    email: str
    password: str
    client_id: str
    redirect_uri: str
    scope: str = Field(default="openid")
    state: str | None = Field(default=None)
    code_challenge: str | None = Field(default=None)
    code_challenge_method: str | None = Field(default=None)


class TokenRequest(BaseModel):
    """POST /token — exchange code for tokens."""

    grant_type: str = Field(description="Must be 'authorization_code'.")
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str | None = Field(default=None)
    code_verifier: str | None = Field(default=None)


class TokenResponse(BaseModel):
    """Returned on successful token exchange."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str = ""

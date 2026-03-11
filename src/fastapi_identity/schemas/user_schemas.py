from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Public-facing user representation — never expose the hash."""

    id: str
    email: str
    is_active: bool
    is_verified: bool


class TokenResponse(BaseModel):
    """Returned on successful login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

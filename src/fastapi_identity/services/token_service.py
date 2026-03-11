from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from fastapi_identity.core.exceptions import TokenExpiredError, InvalidTokenError
from fastapi_identity.core.settings import get_settings


class TokenService:
    """Creates and validates JWT access & refresh tokens."""

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def access_token_expires_in(self) -> int:
        """Access token lifetime in seconds."""
        return self._settings.access_token_expire_minutes * 60

    def create_access_token(self, user_id: str, email: str, extra_claims: dict | None = None) -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self._settings.access_token_expire_minutes)

        payload = {
            "sub": user_id,
            "email": email,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": now,
            "exp": expires,
            "type": "access",
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, self._settings.secret_key, algorithm=self._settings.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=self._settings.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "iss": self._settings.issuer,
            "iat": now,
            "exp": expires,
            "type": "refresh",
        }

        return jwt.encode(payload, self._settings.secret_key, algorithm=self._settings.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT. Raises on expiry or invalid signature."""
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
                audience=self._settings.audience,
                issuer=self._settings.issuer,
            )
            return payload
        except JWTError as e:
            if "expired" in str(e).lower():
                raise TokenExpiredError()
            raise InvalidTokenError()

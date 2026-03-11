from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi_identity.core.exceptions import InvalidTokenError
from fastapi_identity.models.user_model import User
from fastapi_identity.security.claims import ClaimsPrincipal, Claim
from fastapi_identity.services.token_service import TokenService
from fastapi_identity.stores.user_store import UserStore

_security = HTTPBearer()


def require_user(
        store: UserStore,
        token_service: TokenService,
):
    """
    Returns a FastAPI dependency that extracts and validates
    the current user from the Authorization header.

    Usage in your app:
        get_current_user = require_user(store, token_service)
        @app.get("/me")
        async def me(user: User = Depends(get_current_user)):
            ...
    """

    async def _get_current_user(
            credentials: HTTPAuthorizationCredentials = Depends(_security),
    ) -> User:
        payload = token_service.decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise InvalidTokenError()

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        user = await store.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidTokenError()

        return user

    return _get_current_user


def require_principal(
        store: UserStore,
        token_service: TokenService,
):
    """
    Like require_user, but returns a ClaimsPrincipal
    populated with claims from the JWT payload.
    """

    async def _get_principal(
            credentials: HTTPAuthorizationCredentials = Depends(_security),
    ) -> ClaimsPrincipal:
        payload = token_service.decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise InvalidTokenError()

        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            raise InvalidTokenError()

        user = await store.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidTokenError()

        # Build claims from JWT payload
        claims: list[Claim] = []
        for key, value in payload.items():
            if key in ("sub", "exp", "iat", "iss", "aud", "type"):
                continue
            if isinstance(value, list):
                for v in value:
                    claims.append(Claim(type=key, value=str(v)))
            else:
                claims.append(Claim(type=key, value=str(value)))

        return ClaimsPrincipal(user_id=user_id, email=email, claims=claims)

    return _get_principal

import hashlib
import base64
import secrets
from datetime import datetime, timedelta, timezone

from fastapi_identity.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from fastapi_identity.models.authorization_code_model import AuthorizationCode
from fastapi_identity.models.client_model import OAuthClient
from fastapi_identity.schemas.oauth_schemas import TokenResponse
from fastapi_identity.services.password_service import PasswordService
from fastapi_identity.services.token_service import TokenService
from fastapi_identity.stores.authorization_code_store import AuthorizationCodeStore
from fastapi_identity.stores.client_store import ClientStore
from fastapi_identity.stores.user_store import UserStore

AUTHORIZATION_CODE_LIFETIME_SECONDS = 600


class AuthorizationService:
    """Handles the Authorization Code Flow with PKCE."""

    def __init__(
            self,
            user_store: UserStore,
            client_store: ClientStore,
            code_store: AuthorizationCodeStore,
            token_service: TokenService,
    ) -> None:
        self._user_store = user_store
        self._client_store = client_store
        self._code_store = code_store
        self._token_service = token_service

    async def validate_client(
            self, client_id: str, redirect_uri: str, scopes: str
    ) -> OAuthClient:
        """Validate client_id, redirect_uri, and requested scopes."""
        client = await self._client_store.get_by_client_id(client_id)
        if not client or not client.is_active:
            raise InvalidTokenError()

        if redirect_uri not in client.redirect_uris_list:
            raise InvalidTokenError()

        requested = set(scopes.split())
        allowed = set(client.allowed_scopes_list)
        if not requested.issubset(allowed):
            raise InvalidTokenError()

        return client

    async def authenticate_and_issue_code(
            self,
            email: str,
            password: str,
            client_id: str,
            redirect_uri: str,
            scopes: str,
            code_challenge: str | None = None,
            code_challenge_method: str | None = None,
    ) -> str:
        """Authenticate user and return an authorization code."""
        user = await self._user_store.get_by_email(email)
        if not user or not PasswordService.verify(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        code = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)

        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user.id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            created_at=now,
            expires_at=now + timedelta(seconds=AUTHORIZATION_CODE_LIFETIME_SECONDS),
        )

        await self._code_store.save(auth_code)
        return code

    async def exchange_code(
            self,
            code: str,
            client_id: str,
            redirect_uri: str,
            client_secret: str | None = None,
            code_verifier: str | None = None,
    ) -> TokenResponse:
        """Exchange an authorization code for tokens."""
        auth_code = await self._code_store.get_by_code(code)
        if not auth_code:
            raise InvalidTokenError()

        if auth_code.is_used or auth_code.is_expired:
            raise InvalidTokenError()

        if auth_code.client_id != client_id or auth_code.redirect_uri != redirect_uri:
            raise InvalidTokenError()

        # Validate client
        client = await self._client_store.get_by_client_id(client_id)
        if not client or not client.is_active:
            raise InvalidTokenError()

        # Confidential clients must provide valid client_secret
        if not client.is_public:
            if not client_secret or client_secret != client.client_secret:
                raise InvalidTokenError()

        # PKCE verification
        if auth_code.code_challenge:
            if not code_verifier:
                raise InvalidTokenError()
            if not self._verify_pkce(
                    code_verifier, auth_code.code_challenge, auth_code.code_challenge_method
            ):
                raise InvalidTokenError()

        # Mark code as used
        await self._code_store.mark_used(auth_code)

        # Look up user and issue tokens
        user = await self._user_store.get_by_id(auth_code.user_id)
        if not user or not user.is_active:
            raise InvalidTokenError()

        access_token = self._token_service.create_access_token(user.id, user.email)
        refresh_token = self._token_service.create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_service.access_token_expires_in,
            scope=auth_code.scopes,
        )

    @staticmethod
    def _verify_pkce(
            code_verifier: str, code_challenge: str, method: str | None
    ) -> bool:
        """Verify PKCE code_verifier against stored code_challenge."""
        if method == "S256":
            digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
            computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            return computed == code_challenge
        elif method == "plain" or method is None:
            return code_verifier == code_challenge
        return False

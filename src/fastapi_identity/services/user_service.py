from fastapi_identity.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, InvalidTokenError
from fastapi_identity.schemas.user_schemas import UserCreate, TokenResponse
from fastapi_identity.services.password_service import PasswordService
from fastapi_identity.services.token_service import TokenService
from fastapi_identity.stores.user_store import UserStore


class UserService:
    """Orchestrates user registration and authentication."""

    def __init__(self, store: UserStore, token_service: TokenService) -> None:
        self._store = store
        self._token_service = token_service

    async def register(self, data: UserCreate) -> TokenResponse:
        existing = await self._store.get_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError()

        hashed = PasswordService.hash(data.password)
        user = await self._store.create(email=data.email, hashed_password=hashed)

        return self._issue_tokens(user.id, user.email)

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        user = await self._store.get_by_email(email)
        if not user or not PasswordService.verify(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        return self._issue_tokens(user.id, user.email)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self._token_service.decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise InvalidTokenError()

        user_id = payload["sub"]
        user = await self._store.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsError()

        return self._issue_tokens(user.id, user.email)

    def _issue_tokens(self, user_id: str, email: str) -> TokenResponse:
        access_token = self._token_service.create_access_token(user_id, email)
        refresh_token = self._token_service.create_refresh_token(user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_service.access_token_expires_in,
        )

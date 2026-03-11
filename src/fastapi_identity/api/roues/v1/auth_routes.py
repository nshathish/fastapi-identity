from fastapi import APIRouter, Depends

from fastapi_identity.api.dependencies import require_user
from fastapi_identity.core.database import get_session
from fastapi_identity.schemas.user_schemas import TokenResponse, UserCreate, UserLogin, UserRead
from fastapi_identity.services.token_service import TokenService
from fastapi_identity.services.user_service import UserService
from fastapi_identity.stores.sqlmodel import SQLModelUserStore


def create_auth_router(
        token_service: TokenService,
        prefix: str = "/auth",
        tags: list[str] | None = None,
) -> APIRouter:
    """
    Factory that creates an APIRouter with auth endpoints.

    The consumer calls this in their app setup, passing in
    their store and token service instances.
    """

    router = APIRouter(prefix=prefix, tags=tags or ["auth"])

    @router.post("/register", response_model=TokenResponse, status_code=201)
    async def register(data: UserCreate, session=Depends(get_session)):
        store = SQLModelUserStore(session)
        user_service = UserService(store=store, token_service=token_service)
        return await user_service.register(data)

    @router.post("/login", response_model=TokenResponse)
    async def login(data: UserLogin, session=Depends(get_session)):
        store = SQLModelUserStore(session)
        user_service = UserService(store=store, token_service=token_service)
        return await user_service.authenticate(data.email, data.password)

    @router.post("/refresh", response_model=TokenResponse)
    async def refresh(refresh_token: str, session=Depends(get_session)):
        store = SQLModelUserStore(session)
        user_service = UserService(store=store, token_service=token_service)
        return await user_service.refresh(refresh_token)

    @router.get("/me", response_model=UserRead)
    async def me(session=Depends(get_session)):
        store = SQLModelUserStore(session)
        get_current_user = require_user(store, token_service)
        user = await get_current_user()
        return UserRead(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )

    return router

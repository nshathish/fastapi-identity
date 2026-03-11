from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi_identity.core.database import get_session
from fastapi_identity.core.exceptions import InvalidTokenError
from fastapi_identity.schemas.oauth_schemas import (
    AuthorizeLoginRequest,
    TokenRequest,
    TokenResponse,
)
from fastapi_identity.services.authorization_service import AuthorizationService
from fastapi_identity.services.token_service import TokenService
from fastapi_identity.stores.authorization_code_store import AuthorizationCodeStore
from fastapi_identity.stores.client_store import ClientStore
from fastapi_identity.stores.user_store import UserStore


def create_oauth_router(
        token_service: TokenService,
        prefix: str = "/oauth",
        tags: list[str] | None = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags or ["oauth"])

    def _build_auth_service(session: AsyncSession) -> AuthorizationService:
        return AuthorizationService(
            user_store=UserStore(session),
            client_store=ClientStore(session),
            code_store=AuthorizationCodeStore(session),
            token_service=token_service,
        )

    @router.get("/authorize")
    async def authorize(
            response_type: str = Query(...),
            client_id: str = Query(...),
            redirect_uri: str = Query(...),
            scope: str = Query(default="openid"),
            state: str | None = Query(default=None),
            code_challenge: str | None = Query(default=None),
            code_challenge_method: str | None = Query(default=None),
            session: AsyncSession = Depends(get_session),
    ):
        auth_service = _build_auth_service(session)

        if response_type != "code":
            raise InvalidTokenError()

        await auth_service.validate_client(client_id, redirect_uri, scope)

        # In production: render login HTML page
        # For now: return JSON indicating login is required
        return {
            "action": "login_required",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }

    @router.post("/authorize")
    async def authorize_login(
            data: AuthorizeLoginRequest,
            session: AsyncSession = Depends(get_session),
    ):
        auth_service = _build_auth_service(session)

        code = await auth_service.authenticate_and_issue_code(
            email=data.email,
            password=data.password,
            client_id=data.client_id,
            redirect_uri=data.redirect_uri,
            scopes=data.scope,
            code_challenge=data.code_challenge,
            code_challenge_method=data.code_challenge_method,
        )

        redirect_url = f"{data.redirect_uri}?code={code}"
        if data.state:
            redirect_url += f"&state={data.state}"

        return RedirectResponse(url=redirect_url, status_code=302)

    @router.post("/token", response_model=TokenResponse)
    async def token(
            data: TokenRequest,
            session: AsyncSession = Depends(get_session),
    ):
        if data.grant_type != "authorization_code":
            raise InvalidTokenError()

        auth_service = _build_auth_service(session)

        return await auth_service.exchange_code(
            code=data.code,
            client_id=data.client_id,
            redirect_uri=data.redirect_uri,
            client_secret=data.client_secret,
            code_verifier=data.code_verifier,
        )

    return router

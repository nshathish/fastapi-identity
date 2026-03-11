from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi_identity.models.authorization_code_model import AuthorizationCode


class AuthorizationCodeStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, auth_code: AuthorizationCode) -> AuthorizationCode:
        self._session.add(auth_code)
        await self._session.commit()
        await self._session.refresh(auth_code)
        return auth_code

    async def get_by_code(self, code: str) -> AuthorizationCode | None:
        result = await self._session.execute(
            select(AuthorizationCode).where(AuthorizationCode.code == code)
        )
        return result.scalars().first()

    async def mark_used(self, auth_code: AuthorizationCode) -> None:
        auth_code.is_used = True
        self._session.add(auth_code)
        await self._session.commit()

from typing import Any

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from fastapi_identity.models.user_model import User
from fastapi_identity.stores.base import BaseUserStore


class SQLModelUserStore(BaseUserStore):
    """SQLModel/SQLAlchemy-backed user store using AsyncSession."""

    def __init__(self, session: AsyncSession | Any) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self._session.exec(statement)
        return result.first()

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def delete(self, user_id: str) -> bool:
        user = await self._session.get(User, user_id)
        if not user:
            return False
        await self._session.delete(user)
        await self._session.commit()
        return True

from sqlmodel import Session, select

from fastapi_identity.core.database import get_session
from fastapi_identity.models.user_model import User
from fastapi_identity.stores.base import BaseUserStore


class SQLModelUserStore(BaseUserStore):
    """SQLModel/SQLAlchemy-backed user store.

    Accepts a Session factory so the consumer controls
    their own engine and session lifecycle.
    """

    def __init__(self) -> None:
        self._session = get_session()

    async def get_by_id(self, user_id: str) -> User | None:
        return self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self._session.exec(statement).first()

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    async def delete(self, user_id: str) -> bool:
        user = self._session.get(User, user_id)
        if not user:
            return False
        self._session.delete(user)
        self._session.commit()
        return True

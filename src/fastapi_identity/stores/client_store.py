from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi_identity.models.client_model import OAuthClient


class ClientStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_client_id(self, client_id: str) -> OAuthClient | None:
        result = await self._session.execute(
            select(OAuthClient).where(OAuthClient.client_id == client_id)
        )
        return result.scalars().first()

    async def create(self, client: OAuthClient) -> OAuthClient:
        self._session.add(client)
        await self._session.commit()
        await self._session.refresh(client)
        return client

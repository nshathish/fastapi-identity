from abc import ABC, abstractmethod

from fastapi_identity.models.user_model import User


class BaseUserStore(ABC):
    """Abstract interface for user persistence.

        Implement this to plug in any database backend.
        The library ships with a SQLModel implementation,
        but consumers can provide their own.
        """

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """Retrieve a user by their unique ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email address."""
        ...

    @abstractmethod
    async def create(self, email: str, hashed_password: str) -> User:
        """Persist a new user and return the created record."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user record."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user by ID. Returns True if deleted."""
        ...

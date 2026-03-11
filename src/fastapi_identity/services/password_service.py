from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Handles password hashing and verification."""

    @staticmethod
    def hash(password: str) -> str:
        """Hash a plain-text password."""
        return _pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a hash."""
        return _pwd_context.verify(plain_password, hashed_password)

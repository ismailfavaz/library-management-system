"""
Service layer orchestrating User entity business rules and repository access.
"""

from src.library.exceptions import DuplicateEmailError, UserNotFoundError, ValidationError
from src.library.models.entities import User
from src.library.storage.user_repository import UserRepository
from src.library.utils.logger import get_logger
from src.library.utils.security import hash_password, verify_password

logger = get_logger(__name__)


class UserService:
    """Manages User operations and enforces domain constraints."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register_user(
        self,
        name: str,
        email: str,
        phone: str,
        password: str | None = None,
        role: str = "MEMBER",
        max_loans: int = 5,
    ) -> User:
        """Registers a new user with optional password hashing and role.

        Raises:
            DuplicateEmailError: If email address is already registered.
        """
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise DuplicateEmailError(email)

        pwd_hash = hash_password(password) if password else None

        user = User(
            name=name,
            email=email,
            phone=phone,
            role=role,
            password_hash=pwd_hash,
            max_loans=max_loans,
        )
        return self.user_repo.add(user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticates user by email and password.

        Returns:
            User instance if credentials are valid, None otherwise.
        """
        user = self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            return None

        if verify_password(password, user.password_hash):
            logger.info(f"User '{user.email}' authenticated successfully.")
            return user

        logger.warning(f"Failed authentication attempt for email '{email}'.")
        return None

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieves user by ID.

        Raises:
            UserNotFoundError: If user ID does not exist.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def get_all_users(self) -> list[User]:
        """Retrieves all registered users."""
        return self.user_repo.get_all()

    def update_user(
        self,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        max_loans: int | None = None,
    ) -> User:
        """Updates user profile details."""
        user = self.get_user_by_id(user_id)

        if email is not None and email.strip().lower() != user.email:
            existing = self.user_repo.get_by_email(email)
            if existing:
                raise DuplicateEmailError(email)
            user.email = email

        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone
        if max_loans is not None:
            user.max_loans = max_loans

        self.user_repo.update(user)
        return user

    def delete_user(self, user_id: int) -> None:
        """Deletes a user account.

        Raises:
            UserNotFoundError: If user ID is not found.
        """
        self.get_user_by_id(user_id)
        self.user_repo.delete(user_id)

    def search_users(self, query: str) -> list[User]:
        """Searches users matching keyword."""
        return self.user_repo.search(query)

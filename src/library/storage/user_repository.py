"""
Repository pattern implementation for User database operations.
"""

from src.library.exceptions import DatabaseError
from src.library.models.entities import User
from src.library.storage.db import DatabaseManager
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Handles CRUD database operations for User entities."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def add(self, user: User) -> User:
        """Inserts a new user record into the database.

        Args:
            user: Unsaved User instance.

        Returns:
            User instance populated with assigned database primary key ID.
        """
        sql = """
            INSERT INTO users (name, email, phone, max_loans, member_since)
            VALUES (?, ?, ?, ?, ?);
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    user.name,
                    user.email,
                    user.phone,
                    user.max_loans,
                    user.member_since,
                ),
            )
            user.id = cursor.lastrowid
            logger.info(f"User registered in database: '{user.name}' (ID: {user.id})")
            return user

    def get_by_id(self, user_id: int) -> User | None:
        """Retrieves a user record by primary key ID."""
        sql = "SELECT * FROM users WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None

    def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by unique email address."""
        sql = "SELECT * FROM users WHERE email = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email.strip().lower(),))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None

    def get_all(self) -> list[User]:
        """Retrieves all registered users in alphabetical order by name."""
        sql = "SELECT * FROM users ORDER BY name ASC;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [User.from_dict(dict(r)) for r in rows]

    def update(self, user: User) -> bool:
        """Updates user details.

        Returns:
            True if row was updated, False otherwise.
        """
        if user.id is None:
            raise DatabaseError("Cannot update user without an assigned ID.")

        sql = """
            UPDATE users
            SET name = ?, email = ?, phone = ?, max_loans = ?
            WHERE id = ?;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    user.name,
                    user.email,
                    user.phone,
                    user.max_loans,
                    user.id,
                ),
            )
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated user profile ID {user.id}")
            return updated

    def delete(self, user_id: int) -> bool:
        """Deletes a user record by ID.

        Returns:
            True if deleted, False if ID not found.
        """
        sql = "DELETE FROM users WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted user record ID {user_id}")
            return deleted

    def search(self, query: str) -> list[User]:
        """Searches users matching name, email, or phone number."""
        pattern = f"%{query.strip()}%"
        sql = """
            SELECT * FROM users
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY name ASC;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (pattern, pattern, pattern))
            rows = cursor.fetchall()
            return [User.from_dict(dict(r)) for r in rows]

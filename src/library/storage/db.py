"""
SQLite database connection context manager and utility functions.
"""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from src.library.exceptions import DatabaseError
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and connection lifecycle."""

    def __init__(self, db_path: Path | str = "library.db") -> None:
        self.db_path = Path(db_path)
        # Ensure parent folder exists if a directory path is given
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Establishes and returns a configured SQLite connection.

        Returns:
            sqlite3.Connection object with row_factory set to sqlite3.Row.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Enforce foreign key constraints in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as err:
            logger.error(f"Failed to connect to database at {self.db_path}: {err}")
            raise DatabaseError(f"Database connection error: {err}") from err

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing transactional session handling.

        Yields:
            Active sqlite3.Connection with auto-commit/rollback behavior.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as err:
            conn.rollback()
            logger.error(f"Database transaction error (rolled back): {err}")
            raise DatabaseError(f"Database operation failed: {err}") from err
        finally:
            conn.close()

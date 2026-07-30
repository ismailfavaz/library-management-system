"""
Unit tests for database connection management and schema initialization.
"""

from pathlib import Path
import sqlite3
import pytest

from src.library.storage.db import DatabaseManager
from src.library.storage.schema import initialize_database


def test_database_manager_creation(tmp_path: Path) -> None:
    """Verify DatabaseManager connects and retrieves sqlite3.Row rows."""
    db_file = tmp_path / "test_lib.db"
    db_manager = DatabaseManager(db_file)

    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS val;")
        row = cursor.fetchone()
        assert row["val"] == 1


def test_schema_initialization(tmp_path: Path) -> None:
    """Verify tables and indexes are created properly upon schema initialization."""
    db_file = tmp_path / "test_lib.db"
    db_manager = DatabaseManager(db_file)

    initialize_database(db_manager)

    with db_manager.session() as conn:
        cursor = conn.cursor()
        # Query SQLite master table for created tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"] for row in cursor.fetchall()}

        assert "books" in tables
        assert "users" in tables
        assert "loans" in tables


def test_foreign_key_enforcement(tmp_path: Path) -> None:
    """Verify foreign key constraint error when inserting loan with invalid user/book."""
    db_file = tmp_path / "test_lib.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)

    with pytest.raises(Exception):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            # Attempt to insert loan referencing non-existent book and user
            cursor.execute(
                "INSERT INTO loans (book_id, user_id, borrow_date, due_date) VALUES (99, 99, '2026-01-01', '2026-01-15');"
            )

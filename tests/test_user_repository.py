"""
Unit tests for UserRepository CRUD operations and search functionality.
"""

from pathlib import Path
import pytest

from src.library.exceptions import DatabaseError
from src.library.models.entities import User
from src.library.storage.db import DatabaseManager
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository


@pytest.fixture
def user_repo(tmp_path: Path) -> UserRepository:
    """Fixture providing initialized UserRepository."""
    db_file = tmp_path / "test_users.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)
    return UserRepository(db_manager)


def test_add_and_get_user(user_repo: UserRepository) -> None:
    """Verify adding a user assigns ID and allows email/ID lookup."""
    user = User(
        name="Alice Johnson",
        email="alice.j@example.com",
        phone="555-0100",
        max_loans=5,
    )

    saved = user_repo.add(user)
    assert saved.id is not None

    fetched = user_repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.name == "Alice Johnson"

    by_email = user_repo.get_by_email("ALICE.J@EXAMPLE.COM")
    assert by_email is not None
    assert by_email.id == saved.id


def test_duplicate_email_raises_database_error(user_repo: UserRepository) -> None:
    """Verify unique constraint violation on duplicate email insertion."""
    u1 = User(name="User 1", email="duplicate@example.com", phone="123456")
    user_repo.add(u1)

    u2 = User(name="User 2", email="duplicate@example.com", phone="654321")
    with pytest.raises(DatabaseError):
        user_repo.add(u2)


def test_update_and_delete_user(user_repo: UserRepository) -> None:
    """Verify updating profile and deleting user records."""
    user = User(name="Bob Smith", email="bob@example.com", phone="555-0200")
    saved = user_repo.add(user)

    saved.phone = "555-9999"
    assert user_repo.update(saved) is True

    updated = user_repo.get_by_id(saved.id)
    assert updated.phone == "555-9999"

    assert user_repo.delete(saved.id) is True
    assert user_repo.get_by_id(saved.id) is None


def test_search_users(user_repo: UserRepository) -> None:
    """Verify user search by partial name or email."""
    user_repo.add(User(name="Charlie Brown", email="charlie@example.com", phone="11111"))
    user_repo.add(User(name="David Miller", email="david@test.org", phone="22222"))

    results = user_repo.search("Charlie")
    assert len(results) == 1
    assert results[0].email == "charlie@example.com"

    results_domain = user_repo.search("test.org")
    assert len(results_domain) == 1
    assert results_domain[0].name == "David Miller"

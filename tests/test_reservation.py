"""
Unit tests for reservation subsystem.
"""

from pathlib import Path
import pytest

from src.library.exceptions import ValidationError
from src.library.services.book_service import BookService
from src.library.services.reservation_service import ReservationService
from src.library.services.user_service import UserService
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.reservation_repository import ReservationRepository
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository


@pytest.fixture
def res_setup(tmp_path: Path) -> tuple[ReservationService, BookService, UserService]:
    """Fixture providing initialized ReservationService and dependencies."""
    db_file = tmp_path / "test_res.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)

    book_repo = BookRepository(db_manager)
    user_repo = UserRepository(db_manager)
    res_repo = ReservationRepository(db_manager)

    book_service = BookService(book_repo)
    user_service = UserService(user_repo)
    res_service = ReservationService(res_repo, book_repo, user_repo)

    return res_service, book_service, user_service


def test_reserve_book_queue(res_setup: tuple[ReservationService, BookService, UserService]) -> None:
    """Verify placing reservation on hold queue when book has 0 copies available."""
    res_service, book_service, user_service = res_setup

    book = book_service.add_book("Popular Book", "Author", "0-306-40615-2", 2021, total_copies=1)

    # Manually set available copies to 0 (all copies checked out)
    book.available_copies = 0
    book_service.book_repo.update(book)

    u1 = user_service.register_user("User 1", "u1@test.com", "111")
    res1 = res_service.reserve_book(u1.id, book.id)

    assert res1.id is not None
    assert res1.status == "PENDING"

    queue = res_service.get_book_queue(book.id)
    assert len(queue) == 1
    assert queue[0].user_id == u1.id


def test_reserve_available_book_raises_error(res_setup: tuple[ReservationService, BookService, UserService]) -> None:
    """Verify reserving an available book raises ValidationError."""
    res_service, book_service, user_service = res_setup

    book = book_service.add_book("Available Book", "Author", "0-201-63361-2", 2020, total_copies=2)
    user = user_service.register_user("User", "user@test.com", "222")

    with pytest.raises(ValidationError):
        res_service.reserve_book(user.id, book.id)

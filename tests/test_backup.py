"""
Unit tests for BackupService CSV exports and JSON backup/restore routines.
"""

from pathlib import Path
import pytest

from src.library.services.backup_service import BackupService
from src.library.services.book_service import BookService
from src.library.services.borrow_service import BorrowService
from src.library.services.user_service import UserService
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository


@pytest.fixture
def backup_setup(tmp_path: Path) -> tuple[BackupService, BookService, UserService, BorrowService, Path]:
    """Fixture initializing database, services, and backup target directory."""
    db_file = tmp_path / "test_backup.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)

    book_repo = BookRepository(db_manager)
    user_repo = UserRepository(db_manager)
    loan_repo = LoanRepository(db_manager)

    book_service = BookService(book_repo)
    user_service = UserService(user_repo)
    borrow_service = BorrowService(book_repo, user_repo, loan_repo)
    backup_service = BackupService(book_repo, user_repo, loan_repo)

    return backup_service, book_service, user_service, borrow_service, tmp_path


def test_csv_exports(backup_setup: tuple[BackupService, BookService, UserService, BorrowService, Path]) -> None:
    """Verify exporting Books, Users, and Loans to CSV files."""
    backup_service, book_service, user_service, borrow_service, tmp_dir = backup_setup

    b = book_service.add_book("Test Book", "Author", "0-306-40615-2", 2020, 2)
    u = user_service.register_user("User A", "usera@test.com", "111")
    borrow_service.borrow_book(u.id, b.id)

    csv_books = tmp_dir / "books.csv"
    csv_users = tmp_dir / "users.csv"
    csv_loans = tmp_dir / "loans.csv"

    backup_service.export_books_to_csv(csv_books)
    backup_service.export_users_to_csv(csv_users)
    backup_service.export_loans_to_csv(csv_loans)

    assert csv_books.exists()
    assert "Test Book" in csv_books.read_text(encoding="utf-8")

    assert csv_users.exists()
    assert "usera@test.com" in csv_users.read_text(encoding="utf-8")

    assert csv_loans.exists()
    assert str(b.id) in csv_loans.read_text(encoding="utf-8")


def test_json_backup_and_restore(backup_setup: tuple[BackupService, BookService, UserService, BorrowService, Path]) -> None:
    """Verify JSON full backup creation and restoration onto a fresh database."""
    backup_service, book_service, user_service, borrow_service, tmp_dir = backup_setup

    book_service.add_book("Backup Title", "Backup Author", "0-201-63361-2", 2015, 5)
    user_service.register_user("Backup User", "json@backup.com", "999")

    json_file = tmp_dir / "backup.json"
    backup_service.backup_to_json(json_file)
    assert json_file.exists()

    # Create fresh empty database
    new_db_file = tmp_dir / "new_empty.db"
    new_db_mgr = DatabaseManager(new_db_file)
    initialize_database(new_db_mgr)

    new_book_repo = BookRepository(new_db_mgr)
    new_user_repo = UserRepository(new_db_mgr)
    new_loan_repo = LoanRepository(new_db_mgr)

    new_backup_service = BackupService(new_book_repo, new_user_repo, new_loan_repo)
    counts = new_backup_service.restore_from_json(json_file)

    assert counts["imported_books"] == 1
    assert counts["imported_users"] == 1
    assert new_book_repo.get_by_isbn("0201633612") is not None
    assert new_user_repo.get_by_email("json@backup.com") is not None

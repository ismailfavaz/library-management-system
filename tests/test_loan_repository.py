"""
Unit tests for LoanRepository.
"""

from pathlib import Path
import pytest

from src.library.models.entities import Book, Loan, User
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository


@pytest.fixture
def repos(tmp_path: Path) -> tuple[BookRepository, UserRepository, LoanRepository]:
    """Fixture providing initialized repositories."""
    db_file = tmp_path / "test_loans.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)
    return (
        BookRepository(db_manager),
        UserRepository(db_manager),
        LoanRepository(db_manager),
    )


def test_create_and_retrieve_loan(repos: tuple[BookRepository, UserRepository, LoanRepository]) -> None:
    """Verify loan creation and active loan query."""
    book_repo, user_repo, loan_repo = repos

    book = book_repo.add(
        Book(
            title="Refactoring",
            author="Martin Fowler",
            isbn="0-201-48567-2",
            publication_year=1999,
            total_copies=2,
            available_copies=2,
        )
    )
    user = user_repo.add(
        User(name="Jane Doe", email="jane@example.com", phone="12345")
    )

    loan = Loan(
        book_id=book.id,
        user_id=user.id,
        borrow_date="2026-01-01",
        due_date="2026-01-15",
    )
    saved_loan = loan_repo.add(loan)
    assert saved_loan.id is not None

    active_loans = loan_repo.get_active_loans_by_user(user.id)
    assert len(active_loans) == 1
    assert active_loans[0].book_id == book.id

    fetched = loan_repo.get_active_loan_by_book_and_user(book.id, user.id)
    assert fetched is not None
    assert fetched.id == saved_loan.id


def test_update_loan_return_and_fine(repos: tuple[BookRepository, UserRepository, LoanRepository]) -> None:
    """Verify updating return date and fine amount."""
    book_repo, user_repo, loan_repo = repos

    book = book_repo.add(Book(title="Title", author="Author", isbn="0306406152", publication_year=2000, total_copies=1, available_copies=1))
    user = user_repo.add(User(name="User", email="user@test.com", phone="000"))

    loan = loan_repo.add(
        Loan(book_id=book.id, user_id=user.id, borrow_date="2026-01-01", due_date="2026-01-15")
    )

    loan.return_date = "2026-01-18"
    loan.fine_amount = 3.00
    assert loan_repo.update(loan) is True

    updated = loan_repo.get_by_id(loan.id)
    assert updated.return_date == "2026-01-18"
    assert updated.fine_amount == 3.00
    assert len(loan_repo.get_active_loans_by_user(user.id)) == 0

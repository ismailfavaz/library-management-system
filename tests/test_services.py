"""
Unit tests for application business services (BorrowService, BookService, UserService, FineCalculator).
"""

from pathlib import Path
import pytest

from src.library.exceptions import (
    BookNotAvailableError,
    BookNotBorrowedByUserError,
    BookNotFoundError,
    MaxLoansExceededError,
    ValidationError,
)
from src.library.services.book_service import BookService
from src.library.services.borrow_service import BorrowService
from src.library.services.fine_calculator import FineCalculator, FinePolicy
from src.library.services.report_service import ReportService
from src.library.services.user_service import UserService
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.schema import initialize_database
from src.library.storage.user_repository import UserRepository


@pytest.fixture
def services(tmp_path: Path) -> tuple[BookService, UserService, BorrowService, ReportService]:
    """Fixture providing initialized service layer instances."""
    db_file = tmp_path / "test_services.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)

    book_repo = BookRepository(db_manager)
    user_repo = UserRepository(db_manager)
    loan_repo = LoanRepository(db_manager)

    book_service = BookService(book_repo)
    user_service = UserService(user_repo)
    fine_calc = FineCalculator(FinePolicy(daily_rate=2.00, max_fine_cap=20.00))
    borrow_service = BorrowService(book_repo, user_repo, loan_repo, fine_calc)
    report_service = ReportService(book_repo, user_repo, loan_repo)

    return book_service, user_service, borrow_service, report_service


def test_borrow_and_return_flow(services: tuple[BookService, UserService, BorrowService, ReportService]) -> None:
    """Verify complete borrowing and return lifecycle including stock tracking and fine calculation."""
    book_service, user_service, borrow_service, report_service = services

    book = book_service.add_book(
        title="Domain Driven Design",
        author="Eric Evans",
        isbn="0-321-12521-5",
        publication_year=2003,
        total_copies=1,
    )
    user = user_service.register_user(
        name="Alice Architect",
        email="alice@ddd.org",
        phone="123456",
        max_loans=2,
    )

    assert book.available_copies == 1

    # Borrow book
    loan = borrow_service.borrow_book(user.id, book.id, loan_days=7)
    assert loan.book_id == book.id

    # Check updated available copies
    refreshed_book = book_service.get_book_by_id(book.id)
    assert refreshed_book.available_copies == 0

    # Attempt to borrow when no copies available
    with pytest.raises(BookNotAvailableError):
        borrow_service.borrow_book(user.id, book.id)

    # Return book past due date (due date set 7 days after borrow date, simulated return 10 days later -> 3 days overdue)
    loan.due_date = "2026-01-08"
    borrow_service.loan_repo.update(loan)

    returned_loan, fine = borrow_service.return_book(user.id, book.id, return_date_str="2026-01-11")
    assert fine == 6.00  # 3 days overdue * $2.00/day
    assert returned_loan.fine_amount == 6.00

    # Verify stock restored
    restored_book = book_service.get_book_by_id(book.id)
    assert restored_book.available_copies == 1


def test_max_loans_enforcement(services: tuple[BookService, UserService, BorrowService, ReportService]) -> None:
    """Verify user max borrowing limit is strictly enforced."""
    book_service, user_service, borrow_service, _ = services

    b1 = book_service.add_book("Book 1", "Author 1", "0-306-40615-2", 2000, 2)
    b2 = book_service.add_book("Book 2", "Author 2", "0-201-63361-2", 2001, 2)
    b3 = book_service.add_book("Book 3", "Author 3", "0-201-61622-X", 2002, 2)

    user = user_service.register_user("Limit User", "limit@test.com", "555", max_loans=2)

    borrow_service.borrow_book(user.id, b1.id)
    borrow_service.borrow_book(user.id, b2.id)

    with pytest.raises(MaxLoansExceededError):
        borrow_service.borrow_book(user.id, b3.id)


def test_report_service_statistics(services: tuple[BookService, UserService, BorrowService, ReportService]) -> None:
    """Verify summary statistics output from ReportService."""
    book_service, user_service, borrow_service, report_service = services

    book_service.add_book("Python Cookbook", "David Beazley", "978-1-449-34037-7", 2013, 3, genre="Technology")
    user_service.register_user("Reporter", "rep@test.com", "999")

    stats = report_service.get_summary_statistics()
    assert stats["total_titles"] == 1
    assert stats["total_copies"] == 3
    assert stats["total_users"] == 1
    assert stats["genre_distribution"]["Technology"] == 1

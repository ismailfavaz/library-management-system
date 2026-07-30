"""
Unit tests for domain model entities (Book, User, Loan).
"""

import pytest

from src.library.models.entities import Book, Loan, User


def test_book_creation_and_serialization() -> None:
    """Verify Book instantiation, validation, and dictionary conversion."""
    book = Book(
        id=1,
        title="Design Patterns",
        author="Erich Gamma et al.",
        isbn="0-201-63361-2",
        publication_year=1994,
        total_copies=5,
        available_copies=5,
        genre="Software Engineering",
    )

    assert book.id == 1
    assert book.title == "Design Patterns"
    assert book.isbn == "0201633612"
    assert book.is_available is True

    book_dict = book.to_dict()
    assert book_dict["isbn"] == "0201633612"

    reconstructed = Book.from_dict(book_dict)
    assert reconstructed.title == book.title
    assert reconstructed.isbn == book.isbn


def test_book_invalid_copies() -> None:
    """Verify Book raises ValueError when available_copies is negative or > total_copies."""
    with pytest.raises(ValueError):
        Book(
            title="Refactoring",
            author="Martin Fowler",
            isbn="0-201-48567-2",
            publication_year=1999,
            total_copies=3,
            available_copies=5,  # Invalid: available > total
        )


def test_user_creation_and_serialization() -> None:
    """Verify User instantiation, normalization, and dictionary conversion."""
    user = User(
        id=10,
        name="Alice Smith",
        email="Alice.Smith@Example.com",
        phone="555-0199",
        max_loans=3,
    )

    assert user.name == "Alice Smith"
    assert user.email == "alice.smith@example.com"
    assert user.max_loans == 3

    user_dict = user.to_dict()
    reconstructed = User.from_dict(user_dict)
    assert reconstructed.email == user.email


def test_loan_overdue_days_calculation() -> None:
    """Verify Loan overdue days computation logic."""
    loan = Loan(
        id=100,
        book_id=1,
        user_id=10,
        borrow_date="2026-01-01",
        due_date="2026-01-15",
    )

    assert loan.is_active is True
    # Reference date within due window
    assert loan.calculate_overdue_days("2026-01-10") == 0
    # Reference date exactly on due date
    assert loan.calculate_overdue_days("2026-01-15") == 0
    # Reference date 5 days past due
    assert loan.calculate_overdue_days("2026-01-20") == 5

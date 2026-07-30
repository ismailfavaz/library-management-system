"""
Core domain models representing Book, User, and Loan entities.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self

from src.library.utils.validators import (
    validate_email,
    validate_isbn,
    validate_non_empty_string,
    validate_positive_int,
)


@dataclass
class Book:
    """Represents a library book."""

    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int
    available_copies: int
    genre: str = "General"
    id: int | None = None

    def __post_init__(self) -> None:
        """Validate book parameters upon instantiation."""
        self.title = validate_non_empty_string(self.title, "Title")
        self.author = validate_non_empty_string(self.author, "Author")
        self.isbn = validate_isbn(self.isbn)
        self.publication_year = validate_positive_int(self.publication_year, "Publication Year")
        self.total_copies = validate_positive_int(self.total_copies, "Total Copies")
        
        if self.available_copies < 0 or self.available_copies > self.total_copies:
            raise ValueError(
                f"Available copies ({self.available_copies}) cannot be negative or exceed total copies ({self.total_copies})."
            )

    @property
    def is_available(self) -> bool:
        """Returns True if at least one copy is available for borrowing."""
        return self.available_copies > 0

    def to_dict(self) -> dict[str, Any]:
        """Converts object to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "genre": self.genre,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Constructs a Book instance from a dictionary."""
        return cls(
            id=data.get("id"),
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            publication_year=data["publication_year"],
            total_copies=data["total_copies"],
            available_copies=data.get("available_copies", data["total_copies"]),
            genre=data.get("genre", "General"),
        )


@dataclass
class User:
    """Represents a registered library member."""

    name: str
    email: str
    phone: str
    max_loans: int = 5
    id: int | None = None
    member_since: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )

    def __post_init__(self) -> None:
        """Validate user parameters upon instantiation."""
        self.name = validate_non_empty_string(self.name, "Name")
        self.email = validate_email(self.email)
        self.phone = validate_non_empty_string(self.phone, "Phone")
        self.max_loans = validate_positive_int(self.max_loans, "Max Loans")

    def to_dict(self) -> dict[str, Any]:
        """Converts object to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "max_loans": self.max_loans,
            "member_since": self.member_since,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Constructs a User instance from a dictionary."""
        return cls(
            id=data.get("id"),
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            max_loans=data.get("max_loans", 5),
            member_since=data.get(
                "member_since", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            ),
        )


@dataclass
class Loan:
    """Represents a book borrowing transaction."""

    book_id: int
    user_id: int
    borrow_date: str
    due_date: str
    return_date: str | None = None
    fine_amount: float = 0.0
    id: int | None = None

    @property
    def is_active(self) -> bool:
        """Returns True if the book has not been returned yet."""
        return self.return_date is None

    def calculate_overdue_days(self, reference_date_str: str | None = None) -> int:
        """Calculates days overdue relative to due_date.

        Args:
            reference_date_str: Optional date string ('YYYY-MM-DD'). Defaults to current date.

        Returns:
            Number of overdue days (0 if not overdue).
        """
        if not self.is_active and not reference_date_str:
            target_str = self.return_date
        elif reference_date_str:
            target_str = reference_date_str
        else:
            target_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if not target_str:
            return 0

        target_dt = datetime.strptime(target_str[:10], "%Y-%m-%d")
        due_dt = datetime.strptime(self.due_date[:10], "%Y-%m-%d")

        delta = (target_dt - due_dt).days
        return max(0, delta)

    def to_dict(self) -> dict[str, Any]:
        """Converts object to dictionary format."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "fine_amount": self.fine_amount,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Constructs a Loan instance from a dictionary."""
        return cls(
            id=data.get("id"),
            book_id=data["book_id"],
            user_id=data["user_id"],
            borrow_date=data["borrow_date"],
            due_date=data["due_date"],
            return_date=data.get("return_date"),
            fine_amount=float(data.get("fine_amount", 0.0)),
        )

"""
Service layer orchestrating Book entity business rules and repository access.
"""

from src.library.exceptions import BookNotFoundError, ValidationError
from src.library.models.entities import Book
from src.library.storage.book_repository import BookRepository
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class BookService:
    """Manages Book operations and enforces domain constraints."""

    def __init__(self, book_repo: BookRepository) -> None:
        self.book_repo = book_repo

    def add_book(
        self,
        title: str,
        author: str,
        isbn: str,
        publication_year: int,
        total_copies: int,
        genre: str = "General",
    ) -> Book:
        """Creates and stores a new Book.

        Raises:
            ValidationError: If book with identical ISBN already exists.
        """
        # Check for existing ISBN
        existing = self.book_repo.get_by_isbn(isbn)
        if existing:
            raise ValidationError(f"A book with ISBN '{isbn}' already exists: '{existing.title}'.")

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            publication_year=publication_year,
            total_copies=total_copies,
            available_copies=total_copies,
            genre=genre,
        )
        return self.book_repo.add(book)

    def get_book_by_id(self, book_id: int) -> Book:
        """Retrieves book by ID.

        Raises:
            BookNotFoundError: If book ID does not exist.
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id)
        return book

    def get_all_books(self) -> list[Book]:
        """Retrieves all books."""
        return self.book_repo.get_all()

    def update_book(
        self,
        book_id: int,
        title: str | None = None,
        author: str | None = None,
        publication_year: int | None = None,
        total_copies: int | None = None,
        genre: str | None = None,
    ) -> Book:
        """Updates specific fields of an existing book."""
        book = self.get_book_by_id(book_id)

        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if publication_year is not None:
            book.publication_year = publication_year
        if genre is not None:
            book.genre = genre

        if total_copies is not None:
            delta = total_copies - book.total_copies
            new_available = book.available_copies + delta
            if new_available < 0:
                raise ValidationError(
                    f"Cannot reduce total copies to {total_copies}; {book.total_copies - book.available_copies} copies are currently checked out."
                )
            book.total_copies = total_copies
            book.available_copies = new_available

        self.book_repo.update(book)
        return book

    def delete_book(self, book_id: int) -> None:
        """Deletes a book by ID.

        Raises:
            BookNotFoundError: If book ID is not found.
            ValidationError: If book copies are currently checked out.
        """
        book = self.get_book_by_id(book_id)
        if book.available_copies < book.total_copies:
            raise ValidationError(
                f"Cannot delete book '{book.title}'; copies are currently checked out."
            )
        self.book_repo.delete(book_id)

    def search_books(self, query: str) -> list[Book]:
        """Searches books matching keyword."""
        return self.book_repo.search(query)

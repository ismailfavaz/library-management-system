"""
Unit tests for BookRepository CRUD and search functions.
"""

from pathlib import Path
import pytest

from src.library.exceptions import DatabaseError
from src.library.models.entities import Book
from src.library.storage.book_repository import BookRepository
from src.library.storage.db import DatabaseManager
from src.library.storage.schema import initialize_database


@pytest.fixture
def repo(tmp_path: Path) -> BookRepository:
    """Fixture to provide initialized BookRepository with temporary SQLite DB."""
    db_file = tmp_path / "test_books.db"
    db_manager = DatabaseManager(db_file)
    initialize_database(db_manager)
    return BookRepository(db_manager)


def test_add_and_get_book(repo: BookRepository) -> None:
    """Verify adding a book assigns ID and enables retrieval by ID and ISBN."""
    book = Book(
        title="The Pragmatic Programmer",
        author="Andy Hunt, Dave Thomas",
        isbn="0-201-61622-X",
        publication_year=1999,
        total_copies=3,
        available_copies=3,
        genre="Software Engineering",
    )

    saved = repo.add(book)
    assert saved.id is not None

    fetched = repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.title == "The Pragmatic Programmer"

    by_isbn = repo.get_by_isbn("020161622X")
    assert by_isbn is not None
    assert by_isbn.id == saved.id


def test_add_duplicate_isbn_raises_error(repo: BookRepository) -> None:
    """Verify inserting duplicate ISBN triggers DatabaseError."""
    book1 = Book(
        title="Book One",
        author="Author A",
        isbn="978-0-13-235088-4",
        publication_year=2008,
        total_copies=1,
        available_copies=1,
    )
    repo.add(book1)

    book2 = Book(
        title="Book Two",
        author="Author B",
        isbn="978-0-13-235088-4",  # Duplicate ISBN
        publication_year=2010,
        total_copies=2,
        available_copies=2,
    )

    with pytest.raises(DatabaseError):
        repo.add(book2)


def test_update_and_delete_book(repo: BookRepository) -> None:
    """Verify updating and deleting book records."""
    book = Book(
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="978-0-13-449416-6",
        publication_year=2017,
        total_copies=4,
        available_copies=4,
    )
    saved = repo.add(book)

    # Update available copies
    saved.available_copies = 3
    assert repo.update(saved) is True

    updated = repo.get_by_id(saved.id)
    assert updated.available_copies == 3

    # Delete book
    assert repo.delete(saved.id) is True
    assert repo.get_by_id(saved.id) is None


def test_search_books(repo: BookRepository) -> None:
    """Verify keyword search across titles, authors, and genres."""
    repo.add(
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="978-0-13-235088-4",
            publication_year=2008,
            total_copies=2,
            available_copies=2,
            genre="Programming",
        )
    )
    repo.add(
        Book(
            title="Design Patterns",
            author="Erich Gamma",
            isbn="0-201-63361-2",
            publication_year=1994,
            total_copies=5,
            available_copies=5,
            genre="Software Architecture",
        )
    )

    # Search by author keyword
    results = repo.search("Robert")
    assert len(results) == 1
    assert results[0].title == "Clean Code"

    # Search by genre keyword
    results_arch = repo.search("Architecture")
    assert len(results_arch) == 1
    assert results_arch[0].title == "Design Patterns"

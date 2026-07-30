"""
Repository pattern implementation for Book database operations.
"""

from src.library.exceptions import DatabaseError
from src.library.models.entities import Book
from src.library.storage.db import DatabaseManager
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class BookRepository:
    """Handles CRUD database operations for Book entities."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def add(self, book: Book) -> Book:
        """Inserts a new book record into the database.

        Args:
            book: Unsaved Book instance (id is None).

        Returns:
            Book instance populated with assigned database primary key ID.
        """
        sql = """
            INSERT INTO books (title, author, isbn, publication_year, total_copies, available_copies, genre)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    book.title,
                    book.author,
                    book.isbn,
                    book.publication_year,
                    book.total_copies,
                    book.available_copies,
                    book.genre,
                ),
            )
            book.id = cursor.lastrowid
            logger.info(f"Book added to database: '{book.title}' (ID: {book.id})")
            return book

    def get_by_id(self, book_id: int) -> Book | None:
        """Retrieves a book by its primary key ID."""
        sql = "SELECT * FROM books WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (book_id,))
            row = cursor.fetchone()
            return Book.from_dict(dict(row)) if row else None

    def get_by_isbn(self, isbn: str) -> Book | None:
        """Retrieves a book by its unique ISBN."""
        sql = "SELECT * FROM books WHERE isbn = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (isbn,))
            row = cursor.fetchone()
            return Book.from_dict(dict(row)) if row else None

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[Book]:
        """Retrieves stored books in the library database with optional pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        """
        sql = "SELECT * FROM books ORDER BY title ASC"
        params: list[int] = []
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        sql += ";"

        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [Book.from_dict(dict(r)) for r in rows]


    def update(self, book: Book) -> bool:
        """Updates an existing book record.

        Returns:
            True if row was updated, False otherwise.
        """
        if book.id is None:
            raise DatabaseError("Cannot update book without an assigned ID.")

        sql = """
            UPDATE books
            SET title = ?, author = ?, isbn = ?, publication_year = ?,
                total_copies = ?, available_copies = ?, genre = ?
            WHERE id = ?;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    book.title,
                    book.author,
                    book.isbn,
                    book.publication_year,
                    book.total_copies,
                    book.available_copies,
                    book.genre,
                    book.id,
                ),
            )
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated book record ID {book.id}")
            return updated

    def delete(self, book_id: int) -> bool:
        """Deletes a book record by ID.

        Returns:
            True if record was deleted, False if ID was not found.
        """
        sql = "DELETE FROM books WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (book_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted book record ID {book_id}")
            return deleted

    def search(self, query: str) -> list[Book]:
        """Searches books matching title, author, ISBN, or genre (case-insensitive)."""
        return self.search_books(query=query)

    def search_books(
        self,
        query: str = "",
        genre: str | None = None,
        available_only: bool = False,
    ) -> list[Book]:
        """Performs advanced search on books with optional genre filtering and availability constraints.

        Args:
            query: Keyword to search across title, author, or ISBN.
            genre: Optional genre filter.
            available_only: If True, only returns books with available_copies > 0.

        Returns:
            List of matching Book objects.
        """
        conditions = []
        params: list[str | int] = []

        if query and query.strip():
            pattern = f"%{query.strip()}%"
            conditions.append("(title LIKE ? OR author LIKE ? OR isbn LIKE ?)")
            params.extend([pattern, pattern, pattern])

        if genre and genre.strip():
            conditions.append("genre LIKE ?")
            params.append(f"%{genre.strip()}%")

        if available_only:
            conditions.append("available_copies > 0")

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT * FROM books{where_clause} ORDER BY title ASC;"

        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [Book.from_dict(dict(r)) for r in rows]


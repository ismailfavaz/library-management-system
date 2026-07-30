"""
Repository pattern implementation for Loan database operations.
"""

from datetime import datetime, timezone
from src.library.exceptions import DatabaseError
from src.library.models.entities import Loan
from src.library.storage.db import DatabaseManager
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class LoanRepository:
    """Handles CRUD database operations for Loan entities."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def add(self, loan: Loan) -> Loan:
        """Inserts a new borrowing loan record.

        Args:
            loan: Unsaved Loan entity.

        Returns:
            Saved Loan entity populated with assigned database primary key ID.
        """
        sql = """
            INSERT INTO loans (book_id, user_id, borrow_date, due_date, return_date, fine_amount)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    loan.book_id,
                    loan.user_id,
                    loan.borrow_date,
                    loan.due_date,
                    loan.return_date,
                    loan.fine_amount,
                ),
            )
            loan.id = cursor.lastrowid
            logger.info(
                f"Loan created: User ID {loan.user_id} borrowed Book ID {loan.book_id} (Loan ID: {loan.id})"
            )
            return loan

    def get_by_id(self, loan_id: int) -> Loan | None:
        """Retrieves a loan record by primary key ID."""
        sql = "SELECT * FROM loans WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (loan_id,))
            row = cursor.fetchone()
            return Loan.from_dict(dict(row)) if row else None

    def get_active_loans_by_user(self, user_id: int) -> list[Loan]:
        """Retrieves all active loans (not returned) for a specified user."""
        sql = "SELECT * FROM loans WHERE user_id = ? AND return_date IS NULL ORDER BY due_date ASC;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            return [Loan.from_dict(dict(r)) for r in rows]

    def get_active_loan_by_book_and_user(self, book_id: int, user_id: int) -> Loan | None:
        """Retrieves an active loan for a specific book and user."""
        sql = """
            SELECT * FROM loans
            WHERE book_id = ? AND user_id = ? AND return_date IS NULL
            LIMIT 1;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (book_id, user_id))
            row = cursor.fetchone()
            return Loan.from_dict(dict(row)) if row else None

    def get_all_active_loans(self) -> list[Loan]:
        """Retrieves all active unreturned loans in the library system."""
        sql = "SELECT * FROM loans WHERE return_date IS NULL ORDER BY due_date ASC;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Loan.from_dict(dict(r)) for r in rows]

    def get_all(self) -> list[Loan]:
        """Retrieves all loan records (active and returned)."""
        sql = "SELECT * FROM loans ORDER BY id DESC;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Loan.from_dict(dict(r)) for r in rows]

    def update(self, loan: Loan) -> bool:
        """Updates return date and fine amount for a loan record."""
        if loan.id is None:
            raise DatabaseError("Cannot update loan without an assigned ID.")

        sql = """
            UPDATE loans
            SET return_date = ?, fine_amount = ?
            WHERE id = ?;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (loan.return_date, loan.fine_amount, loan.id))
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated loan record ID {loan.id} (Returned: {loan.return_date})")
            return updated

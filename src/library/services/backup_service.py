"""
CSV Export and JSON Backup/Restore services.
"""

import csv
import json
from pathlib import Path
from typing import Any

from src.library.exceptions import LibraryError
from src.library.models.entities import Book, Loan, User
from src.library.storage.book_repository import BookRepository
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.user_repository import UserRepository
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class BackupService:
    """Handles CSV export functionality and JSON database backup/restoration."""

    def __init__(
        self,
        book_repo: BookRepository,
        user_repo: UserRepository,
        loan_repo: LoanRepository,
    ) -> None:
        self.book_repo = book_repo
        self.user_repo = user_repo
        self.loan_repo = loan_repo

    def export_books_to_csv(self, file_path: Path | str) -> Path:
        """Exports all book records to a CSV file."""
        dest = Path(file_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        books = self.book_repo.get_all()

        headers = ["id", "title", "author", "isbn", "publication_year", "total_copies", "available_copies", "genre"]

        with open(dest, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for book in books:
                writer.writerow(book.to_dict())

        logger.info(f"Exported {len(books)} books to CSV: {dest}")
        return dest

    def export_users_to_csv(self, file_path: Path | str) -> Path:
        """Exports all registered users to a CSV file."""
        dest = Path(file_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        users = self.user_repo.get_all()

        headers = ["id", "name", "email", "phone", "max_loans", "member_since"]

        with open(dest, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for user in users:
                writer.writerow(user.to_dict())

        logger.info(f"Exported {len(users)} users to CSV: {dest}")
        return dest

    def export_loans_to_csv(self, file_path: Path | str) -> Path:
        """Exports all loan transactions to a CSV file."""
        dest = Path(file_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        loans = self.loan_repo.get_all()

        headers = ["id", "book_id", "user_id", "borrow_date", "due_date", "return_date", "fine_amount"]

        with open(dest, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for loan in loans:
                writer.writerow(loan.to_dict())

        logger.info(f"Exported {len(loans)} loans to CSV: {dest}")
        return dest

    def backup_to_json(self, file_path: Path | str) -> Path:
        """Exports entire database contents (Books, Users, Loans) into a structured JSON file."""
        dest = Path(file_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0",
            "books": [b.to_dict() for b in self.book_repo.get_all()],
            "users": [u.to_dict() for u in self.user_repo.get_all()],
            "loans": [l.to_dict() for l in self.loan_repo.get_all()],
        }

        with open(dest, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Database backed up to JSON file: {dest}")
        return dest

    def restore_from_json(self, file_path: Path | str) -> dict[str, int]:
        """Restores library state from a JSON backup file into the database.

        Returns:
            Dictionary containing counts of imported entities.
        """
        src = Path(file_path)
        if not src.exists():
            raise LibraryError(f"Backup file not found: '{file_path}'")

        with open(src, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        imported_books = 0
        imported_users = 0
        imported_loans = 0

        # Import Books
        for b_data in data.get("books", []):
            if not self.book_repo.get_by_isbn(b_data["isbn"]):
                book = Book.from_dict(b_data)
                self.book_repo.add(book)
                imported_books += 1

        # Import Users
        for u_data in data.get("users", []):
            if not self.user_repo.get_by_email(u_data["email"]):
                user = User.from_dict(u_data)
                self.user_repo.add(user)
                imported_users += 1

        # Import Loans
        for l_data in data.get("loans", []):
            loan = Loan.from_dict(l_data)
            # Only add loan if referenced book and user exist
            if self.book_repo.get_by_id(loan.book_id) and self.user_repo.get_by_id(loan.user_id):
                if not self.loan_repo.get_by_id(loan.id) if loan.id else True:
                    self.loan_repo.add(loan)
                    imported_loans += 1

        logger.info(
            f"Restored backup from {src}: {imported_books} books, {imported_users} users, {imported_loans} loans."
        )
        return {
            "imported_books": imported_books,
            "imported_users": imported_users,
            "imported_loans": imported_loans,
        }

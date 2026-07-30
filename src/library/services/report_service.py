"""
Reporting and statistics generation service.
"""

from pathlib import Path
from typing import Any
from src.library.storage.book_repository import BookRepository
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.user_repository import UserRepository


class ReportService:
    """Generates library metrics, statistical summaries, and analytical reports."""

    def __init__(
        self,
        book_repo: BookRepository,
        user_repo: UserRepository,
        loan_repo: LoanRepository,
    ) -> None:
        self.book_repo = book_repo
        self.user_repo = user_repo
        self.loan_repo = loan_repo

    def get_summary_statistics(self) -> dict[str, Any]:
        """Calculates high-level inventory, membership, and transaction metrics.

        Returns:
            Dictionary containing system-wide KPI summary.
        """
        books = self.book_repo.get_all()
        users = self.user_repo.get_all()
        all_loans = self.loan_repo.get_all()
        active_loans = [l for l in all_loans if l.is_active]

        total_title_count = len(books)
        total_copies_count = sum(b.total_copies for b in books)
        available_copies_count = sum(b.available_copies for b in books)
        borrowed_copies_count = total_copies_count - available_copies_count

        total_users = len(users)
        total_loans_issued = len(all_loans)
        currently_active_loans = len(active_loans)

        overdue_count = sum(1 for l in active_loans if l.calculate_overdue_days() > 0)
        total_fines_collected = sum(l.fine_amount for l in all_loans)

        # Genre breakdown calculation
        genre_distribution: dict[str, int] = {}
        for b in books:
            genre_distribution[b.genre] = genre_distribution.get(b.genre, 0) + 1

        return {
            "total_titles": total_title_count,
            "total_copies": total_copies_count,
            "available_copies": available_copies_count,
            "borrowed_copies": borrowed_copies_count,
            "total_users": total_users,
            "total_loans_history": total_loans_issued,
            "active_loans": currently_active_loans,
            "overdue_loans": overdue_count,
            "total_fines_collected": round(total_fines_collected, 2),
            "genre_distribution": genre_distribution,
        }

    def get_most_borrowed_books(self, limit: int = 5) -> list[dict[str, Any]]:
        """Retrieves top N most frequently borrowed books.

        Returns:
            List of dictionaries with book details and borrow counts.
        """
        all_loans = self.loan_repo.get_all()
        borrow_counts: dict[int, int] = {}
        for l in all_loans:
            borrow_counts[l.book_id] = borrow_counts.get(l.book_id, 0) + 1

        sorted_book_ids = sorted(borrow_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for book_id, count in sorted_book_ids:
            book = self.book_repo.get_by_id(book_id)
            if book:
                results.append(
                    {
                        "book_id": book.id,
                        "title": book.title,
                        "author": book.author,
                        "isbn": book.isbn,
                        "borrow_count": count,
                    }
                )

        return results

    def export_books_to_csv(self, file_path: str | Path) -> Path:
        """Exports current book inventory to CSV format.

        Args:
            file_path: Path where CSV file will be written.

        Returns:
            Resolved Path object.
        """
        import csv
        books = self.book_repo.get_all()
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Author", "ISBN", "Publication Year", "Total Copies", "Available Copies", "Genre"])
            for b in books:
                writer.writerow([b.id, b.title, b.author, b.isbn, b.publication_year, b.total_copies, b.available_copies, b.genre])

        return target_path

    def export_loans_to_csv(self, file_path: str | Path) -> Path:
        """Exports complete borrowing history to CSV format.

        Args:
            file_path: Path where CSV file will be written.

        Returns:
            Resolved Path object.
        """
        import csv
        loans = self.loan_repo.get_all()
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Loan ID", "Book ID", "User ID", "Borrow Date", "Due Date", "Return Date", "Fine Amount"])
            for l in loans:
                writer.writerow([l.id, l.book_id, l.user_id, l.borrow_date, l.due_date, l.return_date or "N/A", f"{l.fine_amount:.2f}"])

        return target_path


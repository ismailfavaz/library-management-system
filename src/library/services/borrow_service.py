"""
Service orchestrating book borrowing, return workflows, due dates, and fine calculations.
"""

from datetime import datetime, timedelta, timezone
from src.library.exceptions import (
    BookNotAvailableError,
    BookNotBorrowedByUserError,
    BookNotFoundError,
    BorrowError,
    MaxLoansExceededError,
    UserNotFoundError,
)
from src.library.models.entities import Loan
from src.library.services.fine_calculator import FineCalculator
from src.library.storage.book_repository import BookRepository
from src.library.storage.loan_repository import LoanRepository
from src.library.storage.user_repository import UserRepository
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class BorrowService:
    """Manages library loans, returns, due dates, and fine calculations."""

    def __init__(
        self,
        book_repo: BookRepository,
        user_repo: UserRepository,
        loan_repo: LoanRepository,
        fine_calculator: FineCalculator | None = None,
        default_loan_days: int = 14,
    ) -> None:
        self.book_repo = book_repo
        self.user_repo = user_repo
        self.loan_repo = loan_repo
        self.fine_calculator = fine_calculator or FineCalculator()
        self.default_loan_days = default_loan_days

    def borrow_book(
        self,
        user_id: int,
        book_id: int,
        loan_days: int | None = None,
    ) -> Loan:
        """Processes a book borrowing transaction.

        Args:
            user_id: ID of borrowing user.
            book_id: ID of book to borrow.
            loan_days: Loan duration in days (defaults to 14 days).

        Returns:
            Created Loan entity.

        Raises:
            UserNotFoundError: If user_id invalid.
            BookNotFoundError: If book_id invalid.
            BookNotAvailableError: If no copies available.
            MaxLoansExceededError: If user hit max borrowing limit.
            BorrowError: If user already borrowed this specific book.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id)

        if not book.is_available:
            raise BookNotAvailableError(book.title)

        # Check if user already borrowed this book and hasn't returned it
        existing_loan = self.loan_repo.get_active_loan_by_book_and_user(book_id, user_id)
        if existing_loan:
            raise BorrowError(f"User '{user.name}' currently has an active loan for '{book.title}'.")

        # Check max loan limit for user
        active_loans = self.loan_repo.get_active_loans_by_user(user_id)
        if len(active_loans) >= user.max_loans:
            raise MaxLoansExceededError(user.name, user.max_loans)

        duration = loan_days if loan_days is not None else self.default_loan_days
        now_dt = datetime.now(timezone.utc)
        due_dt = now_dt + timedelta(days=duration)

        borrow_date_str = now_dt.strftime("%Y-%m-%d")
        due_date_str = due_dt.strftime("%Y-%m-%d")

        loan = Loan(
            book_id=book_id,
            user_id=user_id,
            borrow_date=borrow_date_str,
            due_date=due_date_str,
        )

        # Decrement available book copies and save
        book.available_copies -= 1
        self.book_repo.update(book)

        # Save loan record
        saved_loan = self.loan_repo.add(loan)
        logger.info(
            f"Book '{book.title}' successfully borrowed by '{user.name}'. Due date: {due_date_str}."
        )
        return saved_loan

    def return_book(
        self,
        user_id: int,
        book_id: int,
        return_date_str: str | None = None,
    ) -> tuple[Loan, float]:
        """Processes a book return transaction and calculates any overdue fines.

        Args:
            user_id: ID of user returning book.
            book_id: ID of book being returned.
            return_date_str: Optional explicit return date ('YYYY-MM-DD'). Defaults to today.

        Returns:
            Tuple of (Updated Loan entity, fine_amount).

        Raises:
            BookNotBorrowedByUserError: If active loan not found.
        """
        loan = self.loan_repo.get_active_loan_by_book_and_user(book_id, user_id)
        if not loan:
            raise BookNotBorrowedByUserError(book_id, user_id)

        ret_date = return_date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        fine = self.fine_calculator.calculate_fine(loan, ret_date)

        loan.return_date = ret_date
        loan.fine_amount = fine
        self.loan_repo.update(loan)

        # Increment available copies in library
        book = self.book_repo.get_by_id(book_id)
        if book:
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            self.book_repo.update(book)

        logger.info(f"Book ID {book_id} returned by User ID {user_id}. Fine accrued: ${fine:.2f}")
        return loan, fine

    def renew_loan(
        self,
        user_id: int,
        book_id: int,
        extension_days: int = 14,
    ) -> Loan:
        """Extends the due date of an active loan by extension_days.

        Args:
            user_id: ID of borrowing user.
            book_id: ID of book being renewed.
            extension_days: Number of days to extend due date. Defaults to 14.

        Returns:
            Updated Loan entity.

        Raises:
            BookNotBorrowedByUserError: If active loan not found.
            BorrowError: If loan is currently overdue.
        """
        loan = self.loan_repo.get_active_loan_by_book_and_user(book_id, user_id)
        if not loan:
            raise BookNotBorrowedByUserError(book_id, user_id)

        if loan.calculate_overdue_days() > 0:
            raise BorrowError("Overdue loans cannot be renewed. Please return the book and resolve accrued fines.")

        current_due_dt = datetime.strptime(loan.due_date[:10], "%Y-%m-%d")
        new_due_dt = current_due_dt + timedelta(days=extension_days)
        loan.due_date = new_due_dt.strftime("%Y-%m-%d")

        self.loan_repo.update(loan)
        logger.info(f"Loan ID {loan.id} renewed for User ID {user_id}. New due date: {loan.due_date}")
        return loan

    def get_user_loans(self, user_id: int) -> list[Loan]:
        """Retrieves active loans for a specific user."""
        return self.loan_repo.get_active_loans_by_user(user_id)

    def get_overdue_loans(self, reference_date_str: str | None = None) -> list[tuple[Loan, int, float]]:
        """Retrieves all currently overdue loans.

        Returns:
            List of tuples: (Loan, overdue_days, estimated_fine).
        """
        active_loans = self.loan_repo.get_all_active_loans()
        overdue_list = []

        for loan in active_loans:
            overdue_days = loan.calculate_overdue_days(reference_date_str)
            if overdue_days > 0:
                fine = self.fine_calculator.calculate_fine(loan, reference_date_str)
                overdue_list.append((loan, overdue_days, fine))

        return overdue_list

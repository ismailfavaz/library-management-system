"""
Service layer orchestrating book hold reservations and queue management.
"""

from src.library.exceptions import BookNotFoundError, UserNotFoundError, ValidationError
from src.library.models.reservation import Reservation
from src.library.storage.book_repository import BookRepository
from src.library.storage.reservation_repository import ReservationRepository
from src.library.storage.user_repository import UserRepository
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class ReservationService:
    """Manages book hold queues and reservation fulfillment."""

    def __init__(
        self,
        reservation_repo: ReservationRepository,
        book_repo: BookRepository,
        user_repo: UserRepository,
    ) -> None:
        self.reservation_repo = reservation_repo
        self.book_repo = book_repo
        self.user_repo = user_repo

    def reserve_book(self, user_id: int, book_id: int) -> Reservation:
        """Places a user on the hold reservation queue for a book.

        Raises:
            UserNotFoundError: If user does not exist.
            BookNotFoundError: If book does not exist.
            ValidationError: If book has available copies or user already reserved it.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id)

        if book.available_copies > 0:
            raise ValidationError(
                f"Book '{book.title}' has {book.available_copies} copy(ies) available. You can borrow it directly!"
            )

        existing = self.reservation_repo.get_pending_by_book(book_id)
        if any(r.user_id == user_id for r in existing):
            raise ValidationError(f"User '{user.name}' already has a pending reservation for '{book.title}'.")

        res = Reservation(book_id=book_id, user_id=user_id)
        saved = self.reservation_repo.add(res)
        logger.info(f"User '{user.name}' placed in hold queue position #{len(existing) + 1} for '{book.title}'.")
        return saved

    def cancel_reservation(self, reservation_id: int) -> bool:
        """Cancels a pending reservation."""
        res = self.reservation_repo.get_by_id(reservation_id)
        if not res or res.status != "PENDING":
            raise ValidationError(f"Reservation ID {reservation_id} is invalid or not in PENDING state.")
        return self.reservation_repo.update_status(reservation_id, "CANCELLED")

    def get_book_queue(self, book_id: int) -> list[Reservation]:
        """Retrieves pending hold queue for a book."""
        return self.reservation_repo.get_pending_by_book(book_id)

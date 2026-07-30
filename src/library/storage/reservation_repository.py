"""
Repository pattern implementation for Reservation database operations.
"""

from src.library.exceptions import DatabaseError
from src.library.models.reservation import Reservation
from src.library.storage.db import DatabaseManager
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


class ReservationRepository:
    """Handles database persistence for book reservations."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    def add(self, reservation: Reservation) -> Reservation:
        """Inserts a new book reservation record."""
        sql = """
            INSERT INTO reservations (book_id, user_id, status, reserved_at)
            VALUES (?, ?, ?, ?);
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    reservation.book_id,
                    reservation.user_id,
                    reservation.status,
                    reservation.reserved_at,
                ),
            )
            reservation.id = cursor.lastrowid
            logger.info(f"Reservation added: User ID {reservation.user_id} reserved Book ID {reservation.book_id}")
            return reservation

    def get_by_id(self, reservation_id: int) -> Reservation | None:
        """Retrieves a reservation by ID."""
        sql = "SELECT * FROM reservations WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (reservation_id,))
            row = cursor.fetchone()
            return Reservation.from_dict(dict(row)) if row else None

    def get_pending_by_book(self, book_id: int) -> list[Reservation]:
        """Retrieves active pending reservations for a book in order of reservation date."""
        sql = """
            SELECT * FROM reservations
            WHERE book_id = ? AND status = 'PENDING'
            ORDER BY reserved_at ASC;
        """
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (book_id,))
            rows = cursor.fetchall()
            return [Reservation.from_dict(dict(r)) for r in rows]

    def get_user_reservations(self, user_id: int) -> list[Reservation]:
        """Retrieves all reservations placed by a user."""
        sql = "SELECT * FROM reservations WHERE user_id = ? ORDER BY reserved_at DESC;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            return [Reservation.from_dict(dict(r)) for r in rows]

    def update_status(self, reservation_id: int, status: str) -> bool:
        """Updates the status of a reservation."""
        sql = "UPDATE reservations SET status = ? WHERE id = ?;"
        with self.db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (status.upper(), reservation_id))
            return cursor.rowcount > 0

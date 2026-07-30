"""
Domain model representing a book hold reservation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self


@dataclass
class Reservation:
    """Represents a book reservation entry in the queue."""

    book_id: int
    user_id: int
    status: str = "PENDING"  # PENDING, FULFILLED, CANCELLED
    id: int | None = None
    reserved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_dict(self) -> dict[str, Any]:
        """Converts object to dictionary representation."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "status": self.status,
            "reserved_at": self.reserved_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Constructs Reservation instance from dictionary."""
        return cls(
            id=data.get("id"),
            book_id=data["book_id"],
            user_id=data["user_id"],
            status=data.get("status", "PENDING"),
            reserved_at=data.get(
                "reserved_at", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            ),
        )

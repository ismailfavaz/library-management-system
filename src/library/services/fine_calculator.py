"""
Fine calculation logic for overdue library loans.
"""

from dataclasses import dataclass
from src.library.models.entities import Loan
from src.library.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FinePolicy:
    """Configurable fine calculation rules."""

    daily_rate: float = 1.00       # Fine amount per day overdue ($/day)
    grace_period_days: int = 0    # Grace period in days before fines accumulate
    max_fine_cap: float = 50.00   # Maximum fine ceiling ($)


class FineCalculator:
    """Calculates fines for overdue loans based on fine policy."""

    def __init__(self, policy: FinePolicy | None = None) -> None:
        self.policy = policy or FinePolicy()

    def calculate_fine(self, loan: Loan, return_date_str: str | None = None) -> float:
        """Calculates total fine amount for a loan given a return or reference date.

        Args:
            loan: Loan entity to evaluate.
            return_date_str: Optional return date string ('YYYY-MM-DD'). Defaults to current date.

        Returns:
            Calculated fine amount rounded to 2 decimal places.
        """
        overdue_days = loan.calculate_overdue_days(return_date_str)

        if overdue_days <= self.policy.grace_period_days:
            return 0.0

        chargeable_days = overdue_days - self.policy.grace_period_days
        raw_fine = chargeable_days * self.policy.daily_rate
        total_fine = min(raw_fine, self.policy.max_fine_cap)

        return round(total_fine, 2)

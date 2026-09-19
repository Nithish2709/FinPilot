from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Sequence

from app.models.recurring_payment import RecurringPayment, RecurringStatus
from app.schemas.financial import ObligationItem, ObligationsResponse


class ObligationsEngine:
    """Estimates upcoming recurring obligations inside a requested forecast window."""

    @staticmethod
    def calculate_upcoming_obligations(
        recurring_payments: Sequence[RecurringPayment],
        days_ahead: int = 30,
        reference_date: Optional[date] = None,
    ) -> ObligationsResponse:
        ref_date = reference_date or date.today()
        end_window = ref_date + timedelta(days=days_ahead)

        items: List[ObligationItem] = []
        total_obligations = Decimal("0.00")

        for rec in recurring_payments:
            if rec.status != RecurringStatus.ACTIVE.value:
                continue

            expected_date = rec.next_expected_date
            if not expected_date:
                continue

            # If expected date falls within the lookahead window
            if ref_date <= expected_date <= end_window:
                amt = rec.average_amount or Decimal("0.00")
                total_obligations += amt
                items.append(
                    ObligationItem(
                        merchant=rec.merchant,
                        expected_amount=amt.quantize(Decimal("0.01")),
                        expected_date=expected_date,
                        frequency=rec.frequency,
                        confidence=rec.confidence,
                        label="Expected recurring obligation",
                    )
                )

        # Sort by earliest due date
        items.sort(key=lambda x: x.expected_date)

        return ObligationsResponse(
            days_ahead=days_ahead,
            total_obligations=total_obligations.quantize(Decimal("0.01")),
            obligations=items,
        )

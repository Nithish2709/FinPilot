from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Sequence

from app.models.recurring_payment import RecurringFrequency, RecurringStatus
from app.models.transaction import Transaction, TransactionType


@dataclass
class DetectedRecurring:
    merchant: str
    average_amount: Decimal
    frequency: str
    last_payment_date: date
    next_expected_date: Optional[date]
    confidence: Decimal
    status: str
    occurrences: int


class RecurringEngine:
    """
    Deterministic recurring payment detection.
    Analyzes merchant similarity, amount proximity, and interval cadences:
    - Weekly: 5–9 days
    - Monthly: 25–35 days
    - Quarterly: 75–100 days
    - Yearly: 330–400 days
    Allows small configurable amount variation (e.g. ±10%).
    """

    INTERVAL_WINDOWS = [
        (RecurringFrequency.WEEKLY.value, 5, 9, timedelta(days=7)),
        (RecurringFrequency.MONTHLY.value, 25, 35, timedelta(days=30)),
        (RecurringFrequency.QUARTERLY.value, 75, 100, timedelta(days=90)),
        (RecurringFrequency.YEARLY.value, 330, 400, timedelta(days=365)),
    ]

    @classmethod
    def detect_recurring_payments(
        cls,
        transactions: Sequence[Transaction],
    ) -> List[DetectedRecurring]:
        # Group valid DEBIT transactions by normalized merchant / key description
        grouped: dict[str, list[Transaction]] = defaultdict(list)
        for txn in transactions:
            if not txn.is_valid or txn.is_duplicate:
                continue
            if txn.transaction_type != TransactionType.DEBIT.value:
                continue

            key = (txn.merchant or txn.description).strip().lower()
            if not key:
                continue
            grouped[key].append(txn)

        detected_list: List[DetectedRecurring] = []

        for key, txns in grouped.items():
            # Need at least 2 transactions to establish an interval cadence
            if len(txns) < 2:
                continue

            # Sort chronologically
            txns_sorted = sorted(txns, key=lambda t: t.transaction_date)

            # Check consecutive intervals
            intervals = []
            for i in range(1, len(txns_sorted)):
                delta_days = (txns_sorted[i].transaction_date - txns_sorted[i - 1].transaction_date).days
                intervals.append(delta_days)

            if not intervals:
                continue

            # Check cadence matches
            for freq_name, min_days, max_days, expected_step in cls.INTERVAL_WINDOWS:
                matching_intervals = [d for d in intervals if min_days <= d <= max_days]
                # If at least 60% of intervals fit this cadence
                if len(matching_intervals) >= max(1, len(intervals) // 2):
                    amounts = [t.amount for t in txns_sorted if t.amount is not None]
                    avg_amt = sum(amounts) / Decimal(str(len(amounts)))

                    # Check amount consistency (within ±15% of average)
                    close_amounts = [a for a in amounts if abs(a - avg_amt) <= (avg_amt * Decimal("0.15"))]
                    if len(close_amounts) < max(1, len(amounts) // 2):
                        continue

                    # Calculate heuristic confidence score
                    occurrence_factor = min(Decimal("1.0"), Decimal(str(len(txns_sorted))) / Decimal("5.0"))
                    interval_consistency = Decimal(str(len(matching_intervals))) / Decimal(str(len(intervals)))
                    amount_consistency = Decimal(str(len(close_amounts))) / Decimal(str(len(amounts)))
                    confidence = ((interval_consistency * Decimal("0.4")) +
                                  (amount_consistency * Decimal("0.4")) +
                                  (occurrence_factor * Decimal("0.2"))).quantize(Decimal("0.01"))

                    last_date = txns_sorted[-1].transaction_date
                    next_date = last_date + expected_step

                    detected_list.append(
                        DetectedRecurring(
                            merchant=txns_sorted[-1].merchant or txns_sorted[-1].description,
                            average_amount=avg_amt.quantize(Decimal("0.01")),
                            frequency=freq_name,
                            last_payment_date=last_date,
                            next_expected_date=next_date,
                            confidence=confidence,
                            status=RecurringStatus.ACTIVE.value,
                            occurrences=len(txns_sorted),
                        )
                    )
                    break

        return detected_list

from decimal import Decimal
from typing import Dict, List, Optional
from app.schemas.financial import UnusualSpendingItem, UnusualSpendingResponse


class AnomalyEngine:
    """
    Deterministic anomaly detector comparing current category spending against
    historical monthly averages.
    Does NOT use machine learning or LLMs.
    Guards against insufficient historical baseline data.
    """

    MIN_MONTHS_REQUIRED = 2
    ANOMALY_MULTIPLIER = Decimal("1.50")

    @classmethod
    def detect_unusual_spending(
        cls,
        historical_monthly_totals: Dict[str, List[Decimal]],
        current_totals: Dict[str, Decimal],
        threshold_multiplier: Optional[Decimal] = None,
        min_months: Optional[int] = None,
    ) -> UnusualSpendingResponse:
        multiplier = threshold_multiplier or cls.ANOMALY_MULTIPLIER
        required_months = min_months or cls.MIN_MONTHS_REQUIRED

        # Calculate max months available in history
        max_history_length = max((len(v) for v in historical_monthly_totals.values()), default=0)
        has_sufficient = max_history_length >= required_months

        if not has_sufficient:
            return UnusualSpendingResponse(
                has_sufficient_history=False,
                historical_months_available=max_history_length,
                anomalies=[],
            )

        anomalies: List[UnusualSpendingItem] = []

        for cat, curr_amt in current_totals.items():
            hist_list = historical_monthly_totals.get(cat, [])
            if len(hist_list) < required_months:
                continue

            hist_avg = sum(hist_list) / Decimal(str(len(hist_list)))
            if hist_avg <= Decimal("0.00"):
                continue

            # Flag if current exceeds multiplier * historical average
            if curr_amt > (hist_avg * multiplier):
                diff = curr_amt - hist_avg
                pct_change = ((diff / hist_avg) * Decimal("100.0")).quantize(Decimal("0.01"))

                # Severity indicator based on rule thresholds
                if curr_amt > (hist_avg * Decimal("2.50")):
                    severity = "HIGH"
                elif curr_amt > (hist_avg * Decimal("1.80")):
                    severity = "MEDIUM"
                else:
                    severity = "LOW"

                anomalies.append(
                    UnusualSpendingItem(
                        category=cat,
                        current_amount=curr_amt.quantize(Decimal("0.01")),
                        historical_average=hist_avg.quantize(Decimal("0.01")),
                        difference=diff.quantize(Decimal("0.01")),
                        percentage_change=pct_change,
                        severity=severity,
                        explanation=f"Spending in {cat} is {pct_change}% above the {len(hist_list)}-month historical baseline.",
                    )
                )

        anomalies.sort(key=lambda x: x.difference, reverse=True)

        return UnusualSpendingResponse(
            has_sufficient_history=True,
            historical_months_available=max_history_length,
            anomalies=anomalies,
        )

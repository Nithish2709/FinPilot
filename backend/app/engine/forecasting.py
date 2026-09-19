from decimal import Decimal
from typing import List


class ForecastingEngine:
    """
    Simple baseline cashflow forecast.
    Does NOT use machine learning or AI models.
    Projects forward based on average recent monthly net cash flow.
    """

    @staticmethod
    def forecast_cashflow(
        current_balance: Decimal,
        recent_monthly_net_cashflows: List[Decimal],
        months_ahead: int = 3,
    ) -> List[dict]:
        if not recent_monthly_net_cashflows:
            avg_flow = Decimal("0.00")
        else:
            avg_flow = sum(recent_monthly_net_cashflows) / Decimal(str(len(recent_monthly_net_cashflows)))

        projections = []
        running_balance = current_balance

        for m in range(1, months_ahead + 1):
            running_balance += avg_flow
            projections.append({
                "month_offset": m,
                "projected_net_change": avg_flow.quantize(Decimal("0.01")),
                "projected_end_balance": running_balance.quantize(Decimal("0.01")),
            })

        return projections

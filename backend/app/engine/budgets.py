from decimal import Decimal
from app.models.budget import Budget
from app.schemas.financial import BudgetStatusResponse


class BudgetEngine:
    """
    Deterministic budget calculation engine.
    Status Threshold Rules:
    - < 80%: ON_TRACK
    - 80% to 100%: NEAR_LIMIT
    - > 100%: OVER_BUDGET
    """

    @staticmethod
    def calculate_budget_status(budget: Budget, spent_amount: Decimal) -> BudgetStatusResponse:
        budget_amt = budget.amount or Decimal("0.00")
        spent = spent_amount.quantize(Decimal("0.01"))
        remaining = (budget_amt - spent).quantize(Decimal("0.01"))

        if budget_amt > Decimal("0.00"):
            pct_used = ((spent / budget_amt) * Decimal("100.0")).quantize(Decimal("0.01"))
        else:
            pct_used = Decimal("100.00") if spent > Decimal("0.00") else Decimal("0.00")

        if pct_used > Decimal("100.0"):
            status = "OVER_BUDGET"
        elif pct_used >= Decimal("80.0"):
            status = "NEAR_LIMIT"
        else:
            status = "ON_TRACK"

        return BudgetStatusResponse(
            id=budget.id,
            user_id=budget.user_id,
            name=budget.name,
            category=budget.category,
            amount=budget.amount,
            period=budget.period,
            start_date=budget.start_date,
            end_date=budget.end_date,
            is_active=budget.is_active if budget.is_active is not None else True,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            spent_amount=spent,
            remaining_amount=remaining,
            percentage_used=pct_used,
            status=status,
        )

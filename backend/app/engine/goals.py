from datetime import date
from decimal import Decimal
from typing import Optional
from app.models.goal import Goal
from app.schemas.financial import GoalProgressResponse


class GoalEngine:
    """
    Deterministic savings goal calculation engine.
    Calculates progress, remaining amounts, and required monthly contributions.
    Does NOT give investment advice.
    """

    @staticmethod
    def calculate_goal_progress(goal: Goal, reference_date: Optional[date] = None) -> GoalProgressResponse:
        ref_date = reference_date or date.today()
        target = goal.target_amount or Decimal("0.00")
        current = goal.current_amount or Decimal("0.00")

        remaining = max(Decimal("0.00"), target - current).quantize(Decimal("0.01"))
        is_completed = current >= target

        if target > Decimal("0.00"):
            pct = min(Decimal("100.00"), (current / target) * Decimal("100.0")).quantize(Decimal("0.01"))
        else:
            pct = Decimal("100.00")

        # Calculate required monthly savings if target_date exists and goal is not yet completed
        required_monthly: Optional[Decimal] = None
        if not is_completed and goal.target_date:
            if goal.target_date > ref_date:
                # Estimate remaining months
                delta_days = (goal.target_date - ref_date).days
                months_remaining = max(Decimal("1.0"), Decimal(str(delta_days)) / Decimal("30.4375"))
                required_monthly = (remaining / months_remaining).quantize(Decimal("0.01"))
            else:
                # Target date has passed or is today
                required_monthly = remaining

        return GoalProgressResponse(
            id=goal.id,
            user_id=goal.user_id,
            name=goal.name,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            target_date=goal.target_date,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            remaining_amount=remaining,
            percentage_complete=pct,
            required_monthly_saving=required_monthly,
            is_completed=is_completed,
        )

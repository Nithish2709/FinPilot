from decimal import Decimal
from typing import Optional
from app.schemas.financial import PurchaseAnalysisResponse, ScenarioDetail


class PurchaseScenarioEngine:
    """
    Deterministic purchase scenario analyzer.
    Strictly calculates numbers and scenarios ("purchase now" vs "wait").
    Does NOT say "BUY" or "DO NOT BUY" and does NOT give financial advice.
    """

    DEFAULT_SAFETY_BUFFER = Decimal("15000.00")

    @classmethod
    def analyze(
        cls,
        current_balance: Decimal,
        upcoming_obligations: Decimal,
        purchase_amount: Decimal,
        safety_buffer: Optional[Decimal] = None,
    ) -> PurchaseAnalysisResponse:
        buffer = safety_buffer if safety_buffer is not None else cls.DEFAULT_SAFETY_BUFFER

        # Scenario 1: Purchase now
        projected_now = current_balance - upcoming_obligations - purchase_amount
        buffer_diff_now = projected_now - buffer

        # Scenario 2: Wait / Defer purchase
        projected_wait = current_balance - upcoming_obligations
        buffer_diff_wait = projected_wait - buffer

        return PurchaseAnalysisResponse(
            current_balance=current_balance.quantize(Decimal("0.01")),
            upcoming_obligations=upcoming_obligations.quantize(Decimal("0.01")),
            purchase_amount=purchase_amount.quantize(Decimal("0.01")),
            safety_buffer=buffer.quantize(Decimal("0.01")),
            projected_balance=projected_now.quantize(Decimal("0.01")),
            buffer_difference=buffer_diff_now.quantize(Decimal("0.01")),
            scenarios={
                "purchase_now": ScenarioDetail(
                    projected_balance=projected_now.quantize(Decimal("0.01")),
                    buffer_difference=buffer_diff_now.quantize(Decimal("0.01")),
                ),
                "wait": ScenarioDetail(
                    projected_balance=projected_wait.quantize(Decimal("0.01")),
                    buffer_difference=buffer_diff_wait.quantize(Decimal("0.01")),
                ),
            },
        )

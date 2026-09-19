from datetime import date
from decimal import Decimal
from typing import Optional, Sequence
from app.models.transaction import Transaction, TransactionType
from app.schemas.financial import CashFlowSummary


class CashFlowEngine:
    """
    Deterministic cashflow calculator.
    Sign / Type Rules:
    - CREDIT: income / inflow
    - DEBIT: expense / outflow
    - REFUND: reversal / inflow
    - TRANSFER: internal transfer (excluded to avoid double-counting)
    - UNKNOWN: excluded
    """

    @staticmethod
    def calculate_cashflow(
        transactions: Sequence[Transaction],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> CashFlowSummary:
        total_income = Decimal("0.00")
        total_expenses = Decimal("0.00")
        total_refunds = Decimal("0.00")
        count = 0

        for txn in transactions:
            # Respect optional date filters if provided in-memory
            if start_date and txn.transaction_date < start_date:
                continue
            if end_date and txn.transaction_date > end_date:
                continue

            # Skip invalid rows or internal transfers
            if not txn.is_valid or txn.is_duplicate:
                continue
            if txn.transaction_type == TransactionType.TRANSFER.value:
                continue

            amt = txn.amount or Decimal("0.00")

            if txn.transaction_type == TransactionType.CREDIT.value:
                total_income += amt
                count += 1
            elif txn.transaction_type == TransactionType.DEBIT.value:
                total_expenses += amt
                count += 1
            elif txn.transaction_type == TransactionType.REFUND.value:
                total_refunds += amt
                count += 1

        net_cashflow = (total_income + total_refunds) - total_expenses

        return CashFlowSummary(
            start_date=start_date,
            end_date=end_date,
            total_income=total_income.quantize(Decimal("0.01")),
            total_expenses=total_expenses.quantize(Decimal("0.01")),
            total_refunds=total_refunds.quantize(Decimal("0.01")),
            net_cashflow=net_cashflow.quantize(Decimal("0.01")),
            transaction_count=count,
        )

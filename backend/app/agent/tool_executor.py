from datetime import date
from decimal import Decimal
from typing import Any, Dict
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.schemas import (
    AnalyzePurchaseArgs,
    BudgetStatusArgs,
    CategorySpendingArgs,
    GoalStatusArgs,
    MonthlySummaryArgs,
    RecurringPaymentsArgs,
    SearchFinancialDocumentsArgs,
    TransactionsArgs,
    UpcomingObligationsArgs,
)
from app.agent.tool_registry import ToolRegistry
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.financial import PurchaseAnalysisRequest
from app.services.financial_service import FinancialService
from app.services.retrieval_service import RetrievalService


class ToolExecutor:
    """
    Executes tools requested by Qwen.
    CRITICAL SECURITY RULE:
    Strictly injects authenticated user_id from the application session.
    Never uses or trusts model-generated user IDs.
    """

    @classmethod
    async def execute(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        tool_def = ToolRegistry.get(tool_name)
        # Validate arguments against Pydantic schema
        validated_args = tool_def.args_schema.model_validate(arguments)

        try:
            if tool_name == "get_monthly_summary":
                args: MonthlySummaryArgs = validated_args
                res = await FinancialService.get_dashboard_summary(db, user_id=user_id, month_str=args.month)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "month": res.month,
                        "cashflow": res.cashflow.model_dump(),
                        "top_categories": [c.model_dump() for c in res.top_categories],
                        "obligations_total": str(res.obligations.total_amount_due),
                    },
                }

            elif tool_name == "get_transactions":
                args: TransactionsArgs = validated_args
                txns, total = await TransactionRepository.list_by_user(
                    db,
                    user_id=user_id,
                    category=args.category,
                    transaction_type=args.transaction_type,
                    limit=args.limit or 20,
                    offset=0,
                )
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "total_count": total,
                        "transactions": [
                            {
                                "id": str(t.id),
                                "date": str(t.transaction_date),
                                "merchant": t.merchant,
                                "amount": str(t.amount),
                                "type": t.transaction_type,
                                "category": t.category,
                            }
                            for t in txns
                        ],
                    },
                }

            elif tool_name == "get_category_spending":
                args: CategorySpendingArgs = validated_args
                res = await FinancialService.get_category_breakdown(db, user_id=user_id, month_str=args.month)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "month": res.month,
                        "total_expenses": str(res.total_expenses),
                        "categories": [c.model_dump() for c in res.categories],
                    },
                }

            elif tool_name == "get_recurring_payments":
                subscriptions = await FinancialService.get_subscriptions(db, user_id=user_id)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "count": len(subscriptions),
                        "subscriptions": [s.model_dump() for s in subscriptions],
                    },
                }

            elif tool_name == "get_upcoming_obligations":
                args: UpcomingObligationsArgs = validated_args
                obligations = await FinancialService.get_upcoming_obligations(
                    db, user_id=user_id, days_ahead=args.days_ahead or 30
                )
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "total_amount_due": str(obligations.total_amount_due),
                        "count": obligations.count,
                        "items": [item.model_dump() for item in obligations.items],
                    },
                }

            elif tool_name == "get_budget_status":
                args: BudgetStatusArgs = validated_args
                budgets = await FinancialService.list_budgets(db, user_id=user_id, month_str=args.month)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "count": len(budgets),
                        "budgets": [b.model_dump() for b in budgets],
                    },
                }

            elif tool_name == "get_goal_status":
                goals = await FinancialService.list_goals(db, user_id=user_id)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "count": len(goals),
                        "goals": [g.model_dump() for g in goals],
                    },
                }

            elif tool_name == "analyze_purchase":
                args: AnalyzePurchaseArgs = validated_args
                req = PurchaseAnalysisRequest(
                    amount=Decimal(str(args.amount)),
                    description=args.category or "Prospective Purchase",
                    purchase_date=date.today(),
                )
                analysis = await FinancialService.analyze_purchase(db, user_id=user_id, req=req)
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": analysis.model_dump(),
                }

            elif tool_name == "search_financial_documents":
                args: SearchFinancialDocumentsArgs = validated_args
                retrieval = RetrievalService()
                search_res = await retrieval.search_documents(
                    db=db,
                    user_id=user_id,
                    query=args.query,
                    top_k=args.top_k or 5,
                )
                return {
                    "tool": tool_name,
                    "success": True,
                    "data": {
                        "query": search_res.query,
                        "results_count": search_res.total_results,
                        "evidence": [
                            {
                                "chunk_id": str(r.chunk_id),
                                "document_id": str(r.document_id),
                                "content": r.content,
                                "score": r.score,
                                "metadata": r.metadata,
                            }
                            for r in search_res.results
                        ],
                    },
                }

            else:
                return {
                    "tool": tool_name,
                    "success": False,
                    "error": f"Tool '{tool_name}' handler not found.",
                }

        except Exception as e:
            return {
                "tool": tool_name,
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.anomalies import AnomalyEngine
from app.engine.budgets import BudgetEngine
from app.engine.cashflow import CashFlowEngine
from app.engine.categories import CategoryEngine
from app.engine.goals import GoalEngine
from app.engine.obligations import ObligationsEngine
from app.engine.purchase import PurchaseScenarioEngine
from app.engine.recurring import RecurringEngine
from app.models.budget import Budget
from app.models.goal import Goal
from app.models.recurring_payment import RecurringPayment
from app.models.transaction import TransactionType
from app.repositories.budget_repository import BudgetRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.recurring_repository import RecurringRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.financial import (
    BudgetCreate,
    BudgetStatusResponse,
    BudgetUpdate,
    CashFlowSummary,
    CategoryBreakdownResponse,
    DashboardResponse,
    DataQualityInfo,
    GoalCreate,
    GoalProgressResponse,
    GoalUpdate,
    ObligationsResponse,
    PurchaseAnalysisRequest,
    PurchaseAnalysisResponse,
    RecurringPaymentResponse,
    UnusualSpendingResponse,
)


class FinancialService:
    """Orchestrates financial calculations and strictly user-scoped queries."""

    # ---------------------------------------------------------
    # Dashboard & Cashflow
    # ---------------------------------------------------------
    @staticmethod
    async def get_dashboard(db: AsyncSession, user_id: uuid.UUID) -> DashboardResponse:
        # Fetch all valid transactions for user
        txns = await TransactionRepository.get_all_valid_by_user(db, user_id=user_id)

        # 1. Calculate overall cashflow / balance basis
        cf_all = CashFlowEngine.calculate_cashflow(txns)

        # 2. Calculate current month cashflow
        today = date.today()
        month_start = today.replace(day=1)
        cf_month = CashFlowEngine.calculate_cashflow(txns, start_date=month_start, end_date=today)

        # 3. Top categories this month
        month_txns = [t for t in txns if t.transaction_date >= month_start]
        cat_breakdown = CategoryEngine.calculate_category_breakdown(month_txns)
        top_cats = [
            {"category": c.category, "amount": c.amount, "percentage": c.percentage}
            for c in cat_breakdown.categories[:5]
        ]

        # 4. Recurring payments & upcoming obligations
        # First sync any newly detected recurring payments
        detected = RecurringEngine.detect_recurring_payments(txns)
        for d in detected:
            await RecurringRepository.upsert_detected(
                db,
                user_id=user_id,
                merchant=d.merchant,
                average_amount=d.average_amount,
                frequency=d.frequency,
                last_payment_date=d.last_payment_date,
                next_expected_date=d.next_expected_date,
                confidence=d.confidence,
                status=d.status,
            )

        saved_recs = await RecurringRepository.get_all_by_user(db, user_id=user_id)
        obligations_res = ObligationsEngine.calculate_upcoming_obligations(
            saved_recs, days_ahead=30, reference_date=today
        )
        obligations_list = [
            {
                "merchant": o.merchant,
                "expected_amount": o.expected_amount,
                "expected_date": o.expected_date.isoformat(),
                "frequency": o.frequency,
            }
            for o in obligations_res.obligations[:5]
        ]

        # 5. Goal progress
        goals = await GoalRepository.get_all_by_user(db, user_id=user_id)
        goal_items = []
        for g in goals:
            prog = GoalEngine.calculate_goal_progress(g, reference_date=today)
            goal_items.append({
                "id": str(prog.id),
                "name": prog.name,
                "target_amount": prog.target_amount,
                "current_amount": prog.current_amount,
                "percentage_complete": prog.percentage_complete,
                "is_completed": prog.is_completed,
            })

        return DashboardResponse(
            current_balance=cf_all.net_cashflow,
            balance_basis="net_cashflow_from_history",
            monthly_income=cf_month.total_income,
            monthly_expenses=cf_month.total_expenses,
            monthly_refunds=cf_month.total_refunds,
            net_cashflow=cf_month.net_cashflow,
            transaction_count=len(txns),
            top_categories=top_cats,
            upcoming_obligations=obligations_list,
            goal_progress=goal_items,
            data_quality=DataQualityInfo(
                source="transaction_history",
                coverage=f"From {txns[0].transaction_date} to {txns[-1].transaction_date}" if txns else "no_data",
                note="Balance basis represents net cash flow over the available uploaded statement history.",
            ),
        )

    # ---------------------------------------------------------
    # Category Analytics
    # ---------------------------------------------------------
    @staticmethod
    async def get_category_breakdown(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> CategoryBreakdownResponse:
        txns = await TransactionRepository.get_all_valid_by_user(
            db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        return CategoryEngine.calculate_category_breakdown(txns)

    # ---------------------------------------------------------
    # Unusual Spending / Anomalies
    # ---------------------------------------------------------
    @staticmethod
    async def get_unusual_spending(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> UnusualSpendingResponse:
        all_txns = await TransactionRepository.get_all_valid_by_user(db, user_id=user_id)
        if not all_txns:
            return UnusualSpendingResponse(
                has_sufficient_history=False,
                historical_months_available=0,
                anomalies=[],
            )

        ref_end = end_date or date.today()
        ref_start = start_date or ref_end.replace(day=1)

        # Partition into historical vs current period
        historical_months: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(lambda: Decimal("0.00")))
        current_totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

        for txn in all_txns:
            if txn.transaction_type != TransactionType.DEBIT.value:
                continue

            amt = txn.amount or Decimal("0.00")
            cat = txn.category or CategoryEngine.classify_keyword(txn.description, txn.merchant)

            if ref_start <= txn.transaction_date <= ref_end:
                current_totals[cat] += amt
            elif txn.transaction_date < ref_start:
                # Key by YYYY-MM
                month_key = f"{txn.transaction_date.year}-{txn.transaction_date.month:02d}"
                historical_months[cat][month_key] += amt

        # Flatten historical totals to lists per category
        hist_lists: dict[str, list[Decimal]] = {}
        for cat, months_dict in historical_months.items():
            hist_lists[cat] = list(months_dict.values())

        return AnomalyEngine.detect_unusual_spending(hist_lists, current_totals)

    # ---------------------------------------------------------
    # Subscriptions & Obligations
    # ---------------------------------------------------------
    @staticmethod
    async def get_subscriptions(db: AsyncSession, user_id: uuid.UUID) -> List[RecurringPaymentResponse]:
        # Refresh detected recurring payments
        txns = await TransactionRepository.get_all_valid_by_user(db, user_id=user_id)
        detected = RecurringEngine.detect_recurring_payments(txns)
        for d in detected:
            await RecurringRepository.upsert_detected(
                db,
                user_id=user_id,
                merchant=d.merchant,
                average_amount=d.average_amount,
                frequency=d.frequency,
                last_payment_date=d.last_payment_date,
                next_expected_date=d.next_expected_date,
                confidence=d.confidence,
                status=d.status,
            )

        recs = await RecurringRepository.get_all_by_user(db, user_id=user_id)
        return [RecurringPaymentResponse.model_validate(r) for r in recs]

    @staticmethod
    async def get_obligations(
        db: AsyncSession,
        user_id: uuid.UUID,
        days_ahead: int = 30,
    ) -> ObligationsResponse:
        recs = await RecurringRepository.get_all_by_user(db, user_id=user_id)
        return ObligationsEngine.calculate_upcoming_obligations(recs, days_ahead=days_ahead)

    # ---------------------------------------------------------
    # Budgets CRUD & Status
    # ---------------------------------------------------------
    @staticmethod
    async def create_budget(db: AsyncSession, user_id: uuid.UUID, data: BudgetCreate) -> BudgetStatusResponse:
        budget = Budget(
            user_id=user_id,
            name=data.name,
            category=data.category,
            amount=data.amount,
            period=data.period,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=True,
        )
        created = await BudgetRepository.create(db, budget)
        spent = await BudgetRepository.get_spent_for_category(
            db, user_id, created.category, created.start_date, created.end_date
        )
        return BudgetEngine.calculate_budget_status(created, spent)

    @staticmethod
    async def get_budgets(db: AsyncSession, user_id: uuid.UUID) -> List[BudgetStatusResponse]:
        budgets = await BudgetRepository.get_all_by_user(db, user_id)
        results = []
        for b in budgets:
            spent = await BudgetRepository.get_spent_for_category(
                db, user_id, b.category, b.start_date, b.end_date
            )
            results.append(BudgetEngine.calculate_budget_status(b, spent))
        return results

    @staticmethod
    async def get_budget_by_id(db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID) -> Optional[BudgetStatusResponse]:
        budget = await BudgetRepository.get_by_id(db, budget_id, user_id)
        if not budget:
            return None
        spent = await BudgetRepository.get_spent_for_category(
            db, user_id, budget.category, budget.start_date, budget.end_date
        )
        return BudgetEngine.calculate_budget_status(budget, spent)

    @staticmethod
    async def update_budget(
        db: AsyncSession,
        budget_id: uuid.UUID,
        user_id: uuid.UUID,
        data: BudgetUpdate,
    ) -> Optional[BudgetStatusResponse]:
        budget = await BudgetRepository.get_by_id(db, budget_id, user_id)
        if not budget:
            return None

        if data.name is not None:
            budget.name = data.name
        if data.category is not None:
            budget.category = data.category
        if data.amount is not None:
            budget.amount = data.amount
        if data.period is not None:
            budget.period = data.period
        if data.start_date is not None:
            budget.start_date = data.start_date
        if data.end_date is not None:
            budget.end_date = data.end_date
        if data.is_active is not None:
            budget.is_active = data.is_active

        updated = await BudgetRepository.update(db, budget)
        spent = await BudgetRepository.get_spent_for_category(
            db, user_id, updated.category, updated.start_date, updated.end_date
        )
        return BudgetEngine.calculate_budget_status(updated, spent)

    @staticmethod
    async def delete_budget(db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await BudgetRepository.delete(db, budget_id, user_id)

    # ---------------------------------------------------------
    # Goals CRUD & Progress
    # ---------------------------------------------------------
    @staticmethod
    async def create_goal(db: AsyncSession, user_id: uuid.UUID, data: GoalCreate) -> GoalProgressResponse:
        goal = Goal(
            user_id=user_id,
            name=data.name,
            target_amount=data.target_amount,
            current_amount=data.current_amount,
            target_date=data.target_date,
        )
        created = await GoalRepository.create(db, goal)
        return GoalEngine.calculate_goal_progress(created)

    @staticmethod
    async def get_goals(db: AsyncSession, user_id: uuid.UUID) -> List[GoalProgressResponse]:
        goals = await GoalRepository.get_all_by_user(db, user_id)
        return [GoalEngine.calculate_goal_progress(g) for g in goals]

    @staticmethod
    async def get_goal_by_id(db: AsyncSession, goal_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GoalProgressResponse]:
        goal = await GoalRepository.get_by_id(db, goal_id, user_id)
        if not goal:
            return None
        return GoalEngine.calculate_goal_progress(goal)

    @staticmethod
    async def update_goal(
        db: AsyncSession,
        goal_id: uuid.UUID,
        user_id: uuid.UUID,
        data: GoalUpdate,
    ) -> Optional[GoalProgressResponse]:
        goal = await GoalRepository.get_by_id(db, goal_id, user_id)
        if not goal:
            return None

        if data.name is not None:
            goal.name = data.name
        if data.target_amount is not None:
            goal.target_amount = data.target_amount
        if data.current_amount is not None:
            goal.current_amount = data.current_amount
        if data.target_date is not None:
            goal.target_date = data.target_date

        updated = await GoalRepository.update(db, goal)
        return GoalEngine.calculate_goal_progress(updated)

    @staticmethod
    async def delete_goal(db: AsyncSession, goal_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await GoalRepository.delete(db, goal_id, user_id)

    # ---------------------------------------------------------
    # Purchase Scenario Analysis
    # ---------------------------------------------------------
    @staticmethod
    async def analyze_purchase(
        db: AsyncSession,
        user_id: uuid.UUID,
        req: PurchaseAnalysisRequest,
    ) -> PurchaseAnalysisResponse:
        # Compute current historical balance
        txns = await TransactionRepository.get_all_valid_by_user(db, user_id=user_id)
        cf = CashFlowEngine.calculate_cashflow(txns)
        current_balance = cf.net_cashflow

        # Compute upcoming obligations within next 30 days
        recs = await RecurringRepository.get_all_by_user(db, user_id=user_id)
        obs_res = ObligationsEngine.calculate_upcoming_obligations(recs, days_ahead=30)
        upcoming_total = obs_res.total_obligations

        return PurchaseScenarioEngine.analyze(
            current_balance=current_balance,
            upcoming_obligations=upcoming_total,
            purchase_amount=req.amount,
            safety_buffer=req.safety_buffer,
        )

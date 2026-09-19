from datetime import date
from decimal import Decimal
import uuid

from app.engine.anomalies import AnomalyEngine
from app.engine.budgets import BudgetEngine
from app.engine.cashflow import CashFlowEngine
from app.engine.categories import CategoryEngine
from app.engine.forecasting import ForecastingEngine
from app.engine.goals import GoalEngine
from app.engine.obligations import ObligationsEngine
from app.engine.purchase import PurchaseScenarioEngine
from app.engine.recurring import RecurringEngine
from app.models.budget import Budget
from app.models.goal import Goal
from app.models.recurring_payment import RecurringFrequency, RecurringPayment, RecurringStatus
from app.models.transaction import Transaction, TransactionType


def make_test_txn(
    amount: str,
    txn_type: str,
    txn_date: date = date(2026, 9, 15),
    description: str = "Test",
    merchant: str = "Test Merchant",
    category: str = None,
    is_valid: bool = True,
    is_duplicate: bool = False,
) -> Transaction:
    return Transaction(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        transaction_date=txn_date,
        description=description,
        merchant=merchant,
        amount=Decimal(amount),
        currency="INR",
        transaction_type=txn_type,
        category=category,
        is_valid=is_valid,
        is_duplicate=is_duplicate,
    )


def test_cashflow_engine():
    txns = [
        make_test_txn("100000.00", TransactionType.CREDIT.value),
        make_test_txn("25000.00", TransactionType.DEBIT.value),
        make_test_txn("5000.00", TransactionType.DEBIT.value),
        make_test_txn("2000.00", TransactionType.REFUND.value),
        make_test_txn("15000.00", TransactionType.TRANSFER.value),  # Must be excluded
        make_test_txn("500.00", TransactionType.UNKNOWN.value),    # Must be excluded
    ]

    cf = CashFlowEngine.calculate_cashflow(txns)
    assert cf.total_income == Decimal("100000.00")
    assert cf.total_expenses == Decimal("30000.00")
    assert cf.total_refunds == Decimal("2000.00")
    # net = (100000 + 2000) - 30000 = 72000
    assert cf.net_cashflow == Decimal("72000.00")
    assert cf.transaction_count == 4


def test_category_engine_breakdown_and_classifier():
    # Test keyword classifier
    assert CategoryEngine.classify_keyword("Swiggy delivery") == "Food"
    assert CategoryEngine.classify_keyword("Uber trip") == "Transport"
    assert CategoryEngine.classify_keyword("Netflix monthly") == "Entertainment"
    assert CategoryEngine.classify_keyword("Electricity power bill") == "Utilities"
    assert CategoryEngine.classify_keyword("Amazon fresh") == "Shopping"
    assert CategoryEngine.classify_keyword("Unknown store purchase") == "Uncategorized"

    # Test category breakdown
    txns = [
        make_test_txn("8500.00", TransactionType.DEBIT.value, description="Zomato orders"),  # Food
        make_test_txn("1500.00", TransactionType.DEBIT.value, description="Starbucks"),      # Food
        make_test_txn("2000.00", TransactionType.DEBIT.value, description="Uber"),           # Transport
    ]
    res = CategoryEngine.calculate_category_breakdown(txns)
    assert res.total_expenses == Decimal("12000.00")
    assert len(res.categories) == 2
    # Food = 10000 / 12000 = 83.33%
    assert res.categories[0].category == "Food"
    assert res.categories[0].amount == Decimal("10000.00")
    assert res.categories[0].percentage == Decimal("83.33")


def test_recurring_engine_monthly_detection():
    # 4 consecutive monthly payments
    txns = [
        make_test_txn("649.00", TransactionType.DEBIT.value, txn_date=date(2026, 6, 5), merchant="Netflix"),
        make_test_txn("649.00", TransactionType.DEBIT.value, txn_date=date(2026, 7, 5), merchant="Netflix"),
        make_test_txn("649.00", TransactionType.DEBIT.value, txn_date=date(2026, 8, 5), merchant="Netflix"),
        make_test_txn("649.00", TransactionType.DEBIT.value, txn_date=date(2026, 9, 5), merchant="Netflix"),
    ]
    detected = RecurringEngine.detect_recurring_payments(txns)
    assert len(detected) == 1
    rec = detected[0]
    assert rec.merchant == "Netflix"
    assert rec.frequency == RecurringFrequency.MONTHLY.value
    assert rec.average_amount == Decimal("649.00")
    assert rec.confidence >= Decimal("0.80")
    assert rec.next_expected_date == date(2026, 10, 5)


def test_recurring_engine_insufficient_history():
    # Only 1 occurrence cannot establish interval cadence
    txns = [make_test_txn("649.00", TransactionType.DEBIT.value, txn_date=date(2026, 9, 5), merchant="Netflix")]
    detected = RecurringEngine.detect_recurring_payments(txns)
    assert len(detected) == 0


def test_obligations_engine():
    recs = [
        RecurringPayment(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            merchant="Broadband",
            average_amount=Decimal("1199.00"),
            frequency="MONTHLY",
            last_payment_date=date(2026, 8, 20),
            next_expected_date=date(2026, 9, 20),
            confidence=Decimal("0.90"),
            status="ACTIVE",
        ),
        RecurringPayment(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            merchant="Yearly Domain",
            average_amount=Decimal("2500.00"),
            frequency="YEARLY",
            last_payment_date=date(2025, 12, 1),
            next_expected_date=date(2026, 12, 1),  # Outside 30 day window
            confidence=Decimal("0.85"),
            status="ACTIVE",
        ),
    ]
    obs = ObligationsEngine.calculate_upcoming_obligations(recs, days_ahead=30, reference_date=date(2026, 9, 1))
    assert len(obs.obligations) == 1
    assert obs.obligations[0].merchant == "Broadband"
    assert obs.total_obligations == Decimal("1199.00")


def test_budget_engine_thresholds():
    b = Budget(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="Dining Out",
        category="Food",
        amount=Decimal("10000.00"),
        period="monthly",
        start_date=date(2026, 9, 1),
    )

    # < 80% => ON_TRACK
    status1 = BudgetEngine.calculate_budget_status(b, Decimal("5000.00"))
    assert status1.status == "ON_TRACK"
    assert status1.remaining_amount == Decimal("5000.00")
    assert status1.percentage_used == Decimal("50.00")

    # 85% => NEAR_LIMIT
    status2 = BudgetEngine.calculate_budget_status(b, Decimal("8500.00"))
    assert status2.status == "NEAR_LIMIT"
    assert status2.remaining_amount == Decimal("1500.00")

    # 110% => OVER_BUDGET
    status3 = BudgetEngine.calculate_budget_status(b, Decimal("11000.00"))
    assert status3.status == "OVER_BUDGET"
    assert status3.remaining_amount == Decimal("-1000.00")


def test_goal_engine_progress_and_completed():
    # Incomplete goal
    g1 = Goal(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="MacBook",
        target_amount=Decimal("120000.00"),
        current_amount=Decimal("30000.00"),
        target_date=date(2026, 12, 19),  # 3 months away from Sep 19
    )
    prog1 = GoalEngine.calculate_goal_progress(g1, reference_date=date(2026, 9, 19))
    assert prog1.percentage_complete == Decimal("25.00")
    assert prog1.remaining_amount == Decimal("90000.00")
    assert prog1.is_completed is False
    assert prog1.required_monthly_saving is not None

    # Completed goal
    g2 = Goal(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="Emergency Fund",
        target_amount=Decimal("50000.00"),
        current_amount=Decimal("55000.00"),
    )
    prog2 = GoalEngine.calculate_goal_progress(g2)
    assert prog2.percentage_complete == Decimal("100.00")
    assert prog2.remaining_amount == Decimal("0.00")
    assert prog2.is_completed is True


def test_anomaly_engine():
    # Insufficient history (needs >= 2 months)
    res_insufficient = AnomalyEngine.detect_unusual_spending(
        historical_monthly_totals={"Food": [Decimal("5000.00")]},
        current_totals={"Food": Decimal("12000.00")},
    )
    assert res_insufficient.has_sufficient_history is False
    assert len(res_insufficient.anomalies) == 0

    # Sufficient history with spike: baseline avg = 7000, current = 15000 (> 1.5x)
    res_spike = AnomalyEngine.detect_unusual_spending(
        historical_monthly_totals={"Food": [Decimal("7000.00"), Decimal("7500.00"), Decimal("6500.00")]},
        current_totals={"Food": Decimal("15000.00")},
    )
    assert res_spike.has_sufficient_history is True
    assert len(res_spike.anomalies) == 1
    assert res_spike.anomalies[0].category == "Food"
    assert res_spike.anomalies[0].severity in {"MEDIUM", "HIGH"}


def test_purchase_scenario_engine_no_buy_recommendation():
    res = PurchaseScenarioEngine.analyze(
        current_balance=Decimal("85000.00"),
        upcoming_obligations=Decimal("22000.00"),
        purchase_amount=Decimal("60000.00"),
        safety_buffer=Decimal("15000.00"),
    )
    # 85000 - 22000 - 60000 = 3000
    assert res.projected_balance == Decimal("3000.00")
    assert res.buffer_difference == Decimal("-12000.00")
    assert res.scenarios["purchase_now"].projected_balance == Decimal("3000.00")
    assert res.scenarios["wait"].projected_balance == Decimal("63000.00")
    # Verify no subjective BUY / DO NOT BUY text is in output
    assert not hasattr(res, "recommendation")


def test_empty_dataset_handling():
    # Empty transaction dataset
    cf_empty = CashFlowEngine.calculate_cashflow([])
    assert cf_empty.total_income == Decimal("0.00")
    assert cf_empty.total_expenses == Decimal("0.00")
    assert cf_empty.total_refunds == Decimal("0.00")
    assert cf_empty.net_cashflow == Decimal("0.00")
    assert cf_empty.transaction_count == 0

    # Empty category breakdown
    cat_empty = CategoryEngine.calculate_category_breakdown([])
    assert cat_empty.total_expenses == Decimal("0.00")
    assert len(cat_empty.categories) == 0

    # Empty recurring
    rec_empty = RecurringEngine.detect_recurring_payments([])
    assert len(rec_empty) == 0

    # Empty obligations
    obs_empty = ObligationsEngine.calculate_upcoming_obligations([])
    assert obs_empty.total_obligations == Decimal("0.00")
    assert len(obs_empty.obligations) == 0


def test_category_breakdown_zero_division():
    # Only zero-amount transactions
    txns = [make_test_txn("0.00", TransactionType.DEBIT.value, description="Free item")]
    res = CategoryEngine.calculate_category_breakdown(txns)
    assert res.total_expenses == Decimal("0.00")
    if res.categories:
        assert res.categories[0].percentage == Decimal("0.00")


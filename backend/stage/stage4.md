We are continuing development of the FinPilot personal finance application.

STAGE 1 — Project Foundation
STAGE 2 — Database + Authentication
STAGE 3 — Financial Data Ingestion

are already implemented.

Now implement ONLY:

STAGE 4 — FINANCIAL INTELLIGENCE ENGINE

Do not implement RAG, LLM, agents, chat, embeddings, API fallback, or frontend integration yet.

==================================================
CORE ARCHITECTURE PRINCIPLE
==================================================

The Financial Intelligence Engine must work completely WITHOUT an LLM.

LLM will be introduced later only for:

- natural-language understanding
- intent detection
- entity extraction
- tool selection
- explanation

The backend engine must perform:

- financial calculations
- aggregation
- recurring detection
- anomaly detection
- budget calculations
- goal calculations
- cash-flow analysis
- purchase scenario analysis

Never ask an LLM to calculate financial totals.

Use Decimal for monetary calculations.

==================================================
STAGE 4 OBJECTIVE
==================================================

Transform raw transactions into structured financial intelligence.

Input:

PostgreSQL transactions

Output:

- monthly summaries
- category summaries
- recurring payments
- upcoming obligations
- budget status
- goal progress
- unusual spending
- cash-flow information
- purchase scenarios

==================================================
IMPORTANT DATA RULE
==================================================

All financial calculations must use authenticated user data.

Every query must be scoped by:

current_user.id

Never accept user_id from the frontend as an ownership mechanism.

==================================================
TRANSACTION SIGN CONVENTION
==================================================

Do not rely only on amount sign.

Use:

transaction_type

DEBIT:
    expense/outflow

CREDIT:
    income/inflow

REFUND:
    inflow/reversal related to previous purchase

TRANSFER:
    internal movement of money

UNKNOWN:
    excluded from calculations unless explicitly handled

Document the calculation rules.

Do not double-count internal transfers as income or expenses.

==================================================
DATABASE ADDITIONS
==================================================

Stage 4 requires these new models:

Budget
Goal
RecurringPayment

Do not create unnecessary additional tables.

--------------------------------------------------
BUDGET
--------------------------------------------------

Create:

id
user_id
name
category
amount
period
start_date
end_date
is_active
created_at
updated_at

Example:

Food
₹10,000
monthly

Use Decimal.

--------------------------------------------------
GOAL
--------------------------------------------------

Create:

id
user_id
name
target_amount
current_amount
target_date
created_at
updated_at

Use Decimal.

Examples:

Emergency Fund
Laptop
Education

The goal system must track progress, not give investment advice.

--------------------------------------------------
RECURRING PAYMENT
--------------------------------------------------

Create:

id
user_id
merchant
average_amount
frequency
last_payment_date
next_expected_date
confidence
status
created_at
updated_at

Possible frequency:

WEEKLY
MONTHLY
QUARTERLY
YEARLY
UNKNOWN

Possible status:

ACTIVE
INACTIVE
UNKNOWN

Use Decimal.

==================================================
ALEMBIC
==================================================

Create migrations for:

budgets
goals
recurring_payments

Do not use create_all().

==================================================
ENGINE DESIGN
==================================================

Create:

app/engine/

Files:

cashflow.py
categories.py
recurring.py
anomalies.py
budgets.py
goals.py
purchase.py
forecasting.py

Each engine should contain deterministic functions.

Avoid HTTP/FastAPI logic inside engine modules.

For example:

calculate_monthly_summary(...)
calculate_category_summary(...)
detect_recurring_payments(...)
detect_unusual_spending(...)
calculate_budget_status(...)
calculate_goal_progress(...)
analyze_purchase_scenario(...)

==================================================
CASH FLOW ENGINE
==================================================

Implement monthly cash-flow calculations.

Input:

user_id
start_date
end_date

Calculate:

total_income
total_expenses
total_refunds
net_cashflow
transaction_count

Rules:

income =
    CREDIT transactions

expenses =
    DEBIT transactions

refunds =
    REFUND transactions

Do not count TRANSFER as income/expense.

Return:

{
    "total_income": "...",
    "total_expenses": "...",
    "total_refunds": "...",
    "net_cashflow": "...",
    "transaction_count": 123
}

Use Decimal.

==================================================
MONTHLY SUMMARY
==================================================

Implement:

GET /api/v1/dashboard

Require authentication.

Return:

current_balance
monthly_income
monthly_expenses
monthly_refunds
net_cashflow
upcoming_obligations
goal_progress
top_categories

Do not calculate current balance by simply summing arbitrary transaction history unless the account model supports a reliable opening balance.

If transaction history is incomplete:

expose data coverage limitations.

Do not pretend incomplete history is a complete account balance.

==================================================
CATEGORY ANALYSIS
==================================================

Implement category aggregation.

Example:

Food:
    ₹8,500

Transport:
    ₹3,200

Shopping:
    ₹12,000

Bills:
    ₹6,300

Return:

category
amount
percentage
transaction_count

Percentage:

category_expense / total_expenses * 100

Use Decimal.

Avoid division by zero.

==================================================
CATEGORY ENDPOINT
==================================================

Create:

GET /api/v1/analytics/categories

Parameters:

start_date
end_date

Return category breakdown.

Do not use LLM categorization.

Stage 3 transactions may have category=null.

For transactions without categories:

category = "Uncategorized"

Do not invent categories.

==================================================
BASIC RULE-BASED CATEGORIZATION
==================================================

Implement a small deterministic categorization system.

Use merchant/description keyword rules.

Examples:

"swiggy"
"zomato"
"restaurant"
"food"

→ Food

"uber"
"ola"
"metro"
"fuel"

→ Transport

"netflix"
"spotify"
"prime video"

→ Entertainment/Subscription

"electricity"
"water bill"
"internet"

→ Utilities

"amazon"
"flipkart"
"myntra"

→ Shopping

"salary"
"payroll"

→ Income

IMPORTANT:

Only use this deterministic classifier when category is missing.

Do not overwrite an existing category.

Store a category confidence if the schema supports it.

If no rule matches:

Uncategorized

Do not use an LLM in this stage.

==================================================
RECURRING PAYMENT DETECTION
==================================================

Implement deterministic recurring transaction detection.

Do not simply mark every repeated merchant as recurring.

Consider:

merchant similarity
amount similarity
payment intervals
transaction frequency

Example:

Netflix:

2026-06-05 ₹649
2026-07-05 ₹649
2026-08-05 ₹649
2026-09-05 ₹649

This is likely monthly recurring.

Possible interval tolerance:

Monthly:
25–35 days

Weekly:
5–9 days

Quarterly:
75–100 days

Yearly:
330–400 days

Use configurable tolerances.

Amount similarity should allow small variation.

Example:

₹999
₹999
₹1,049

may still represent a recurring service.

Do not hard-code an absolute rule that identical amounts are required.

==================================================
RECURRING CONFIDENCE
==================================================

Calculate deterministic confidence.

For example, based on:

frequency consistency
amount consistency
merchant consistency
number of occurrences

Do not pretend this is a statistically calibrated probability.

If returning confidence:

describe it as an internal heuristic score.

For example:

0.92

means strong pattern according to the implemented heuristic.

==================================================
RECURRING ENDPOINT
==================================================

Create:

GET /api/v1/subscriptions

Return:

merchant
average_amount
frequency
last_payment_date
next_expected_date
confidence
status

Only return recurring records for authenticated user.

==================================================
UPCOMING OBLIGATIONS
==================================================

Use recurring payments to estimate upcoming recurring obligations.

For each active recurring payment:

next_expected_date

If next_expected_date falls inside requested window:

include it.

Create:

GET /api/v1/obligations

Parameters:

days_ahead

Default:

30

Return:

merchant
expected_amount
expected_date
confidence

Clearly label these as expected recurring obligations.

Do not claim certainty.

==================================================
UNUSUAL SPENDING DETECTION
==================================================

Implement deterministic anomaly detection.

Do NOT use an LLM.

Use historical baseline.

For a category:

Calculate historical average spending.

Compare current period.

Example:

Historical monthly food:
₹7,000
₹7,500
₹8,000
₹7,200

Average:
₹7,425

Current:
₹15,000

Flag as unusual.

Use a configurable threshold.

For example:

current > historical_average * 1.5

or a z-score if enough historical data exists.

Do not produce an anomaly when there is insufficient historical data.

Minimum history should be configurable.

Return:

category
current_amount
historical_average
difference
percentage_change
severity

Severity should be descriptive:

LOW
MEDIUM
HIGH

Document that severity is a statistical/rule-based indicator, not a financial judgment.

==================================================
ANOMALY ENDPOINT
==================================================

Create:

GET /api/v1/analytics/unusual-spending

Parameters:

start_date
end_date

Return detected unusual spending categories/transactions.

==================================================
BUDGET ENGINE
==================================================

Implement:

calculate_budget_status()

For each budget:

budget_amount
spent_amount
remaining_amount
percentage_used
status

Status:

ON_TRACK
NEAR_LIMIT
OVER_BUDGET

Example:

Budget:
₹10,000

Spent:
₹8,500

Remaining:
₹1,500

Percentage:
85%

NEAR_LIMIT

Define thresholds explicitly.

For example:

< 80%
ON_TRACK

80–100%
NEAR_LIMIT

> 100%
OVER_BUDGET

These are application thresholds, not financial advice.

==================================================
BUDGET API
==================================================

Create:

POST /api/v1/budgets

GET /api/v1/budgets

GET /api/v1/budgets/{budget_id}

PUT /api/v1/budgets/{budget_id}

DELETE /api/v1/budgets/{budget_id}

All require authentication.

Never allow cross-user access.

==================================================
GOAL ENGINE
==================================================

Implement:

calculate_goal_progress()

Return:

target_amount
current_amount
remaining_amount
percentage_complete
target_date
required_monthly_saving

If target_date exists:

required_monthly_saving =
    remaining_amount / months_remaining

Handle zero/negative remaining amount safely.

If goal is already complete:

remaining_amount = 0

percentage_complete = 100

Do not provide investment recommendations.

==================================================
GOAL API
==================================================

Create:

POST /api/v1/goals

GET /api/v1/goals

GET /api/v1/goals/{goal_id}

PUT /api/v1/goals/{goal_id}

DELETE /api/v1/goals/{goal_id}

Require authentication.

Ensure strict user ownership.

==================================================
PURCHASE SCENARIO ENGINE
==================================================

Create:

POST /api/v1/purchases/analyze

Request:

{
    "amount": 60000,
    "purchase_date": "2026-10-01",
    "description": "Laptop"
}

The engine must NOT say:

BUY
DO NOT BUY

Instead calculate scenarios.

Calculate:

current_balance
upcoming_obligations
projected_balance
safety_buffer
buffer_difference

Example:

current_balance = 85000
upcoming_obligations = 22000
purchase = 60000
safety_buffer = 15000

purchase scenario:

85000 - 22000 - 60000
= 3000

wait scenario:

85000 - 22000
= 63000

Return structured information.

The final API may include:

{
    "current_balance": 85000,
    "upcoming_obligations": 22000,
    "purchase_amount": 60000,
    "projected_balance": 3000,
    "safety_buffer": 15000,
    "buffer_difference": -12000,
    "scenario": {
        "purchase_now": {
            "projected_balance": 3000
        },
        "wait": {
            "projected_balance": 63000
        }
    }
}

Do not provide an overall recommendation.

Do not use an LLM.

==================================================
CURRENT BALANCE
==================================================

Be careful.

Transaction history does not always contain a reliable opening balance.

If account balance data is unavailable:

do not pretend the computed balance is exact.

Use a clearly documented calculation such as:

net cash flow over the available transaction period

and expose:

balance_basis = "transaction_history"

or similar.

If an account has a known starting balance, use:

starting_balance + net_cashflow

Document the assumption.

==================================================
FORECASTING
==================================================

Implement only a simple baseline.

Do NOT use machine learning.

Possible method:

average recent monthly net cashflow.

Use scenarios rather than false precision.

Example:

current balance
+
average monthly net cashflow

Do not claim the forecast is guaranteed.

Create internal function:

forecast_cashflow(...)

Do not create a sophisticated ML forecasting model.

==================================================
FINANCIAL SERVICE
==================================================

Create:

app/services/financial_service.py

It should orchestrate engine components.

For example:

get_monthly_summary()
get_category_summary()
get_recurring_payments()
get_upcoming_obligations()
get_budget_status()
get_goal_progress()
get_unusual_spending()
analyze_purchase()

Keep HTTP handling inside API routes.

Keep calculations inside engine modules.

==================================================
REPOSITORY
==================================================

Create:

transaction_repository.py

It should provide reusable database queries.

Examples:

get_transactions_for_user()
get_transactions_by_date_range()
get_expenses()
get_income()
get_category_totals()
get_recent_transactions()

All must require user scope.

Avoid constructing raw SQL from user input.

==================================================
API ENDPOINTS
==================================================

Create:

GET /api/v1/dashboard

GET /api/v1/analytics/categories

GET /api/v1/analytics/unusual-spending

GET /api/v1/subscriptions

GET /api/v1/obligations

POST /api/v1/budgets

GET /api/v1/budgets

GET /api/v1/budgets/{id}

PUT /api/v1/budgets/{id}

DELETE /api/v1/budgets/{id}

POST /api/v1/goals

GET /api/v1/goals

GET /api/v1/goals/{id}

PUT /api/v1/goals/{id}

DELETE /api/v1/goals/{id}

POST /api/v1/purchases/analyze

==================================================
RESPONSE DESIGN
==================================================

Responses must be structured JSON.

Do not return LLM-generated prose.

Example dashboard:

{
    "period": {
        "start_date": "...",
        "end_date": "..."
    },
    "income": "...",
    "expenses": "...",
    "refunds": "...",
    "net_cashflow": "...",
    "transaction_count": 100,
    "top_categories": [],
    "upcoming_obligations": [],
    "data_quality": {
        "source": "transaction_history",
        "coverage": "available_period"
    }
}

==================================================
DATA QUALITY
==================================================

Every financial response should avoid implying more certainty than the data supports.

Track where appropriate:

data_source
period
transaction_count
coverage

If the user only uploaded one month:

do not describe it as a complete long-term spending history.

If anomaly detection has only one month:

do not claim historical anomaly detection is reliable.

==================================================
TESTING
==================================================

Create comprehensive tests.

Test:

1. Monthly income calculation.

2. Monthly expense calculation.

3. Refund calculation.

4. Transfers excluded.

5. Category aggregation.

6. Category percentages.

7. Uncategorized handling.

8. Rule-based categorization.

9. Recurring monthly payment detection.

10. Recurring weekly payment detection.

11. Recurring amount variation.

12. Insufficient recurring history.

13. Upcoming obligations.

14. Budget percentage.

15. Budget remaining amount.

16. Budget status thresholds.

17. Goal progress.

18. Goal remaining amount.

19. Goal monthly saving requirement.

20. Completed goal.

21. Unusual spending detection.

22. Insufficient history for anomaly detection.

23. Purchase scenario calculation.

24. Safety buffer calculation.

25. No BUY/DO NOT BUY recommendation.

26. User A cannot access User B's budgets.

27. User A cannot access User B's goals.

28. User A cannot access User B's recurring payments.

29. User A cannot access User B's analytics.

30. Decimal precision.

31. Zero division handling.

32. Empty transaction dataset.

33. Stage 1 tests still pass.

34. Stage 2 tests still pass.

35. Stage 3 tests still pass.

==================================================
EDGE CASES
==================================================

Handle:

- zero expenses
- zero income
- no transactions
- only income
- only expenses
- refunds without purchases
- duplicate transactions
- negative amounts
- future-dated transactions
- missing categories
- missing merchants
- missing account
- incomplete history
- completed goals
- budgets with zero amount
- purchase greater than available balance
- no upcoming obligations
- insufficient history for anomaly detection

Do not crash.

==================================================
PERFORMANCE
==================================================

Avoid loading all historical transactions into Python when SQL aggregation can perform the operation efficiently.

Use database aggregation for:

SUM
COUNT
GROUP BY

Use indexes created in previous stages.

Use Python engine logic for calculations that genuinely require application logic.

==================================================
SECURITY
==================================================

Every financial endpoint must:

- require authentication
- use current_user.id
- scope all database queries
- never accept arbitrary user_id
- never expose another user's data

==================================================
NO LLM
==================================================

Do not import:

OpenAI
Gemini
Ollama
LangChain
LlamaIndex

Do not implement RAG.

The entire Stage 4 financial engine must work without AI.

==================================================
FINAL VERIFICATION
==================================================

After implementation:

1. Show final directory tree.

2. Show new database models.

3. Show Alembic migration.

4. Explain each engine.

5. Demonstrate sample dashboard response.

6. Demonstrate category analysis.

7. Demonstrate recurring detection.

8. Demonstrate anomaly detection.

9. Demonstrate budget calculation.

10. Demonstrate goal calculation.

11. Demonstrate purchase scenario.

12. Demonstrate user isolation.

13. Run all tests.

14. Confirm Stage 1, 2 and 3 tests still pass.

15. Report limitations and assumptions.

STOP AFTER STAGE 4.

Do not implement:

- chat
- RAG
- embeddings
- LLM
- agents
- API fallback
- frontend integration
-hardcode anything logic
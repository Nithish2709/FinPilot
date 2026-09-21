Implement **Stage 8 — API LLM Fallback + Reliability** for the existing FinPilot backend.

IMPORTANT:

Stages 1–7 already exist.

Do NOT redesign the existing architecture.

Do NOT change the financial engine.

Do NOT create duplicate tools.

Do NOT create a second financial calculation system.

Do NOT implement frontend changes.

Do NOT implement deployment.

The current local model is:

Qwen1.5-1B-Instruct

The system must continue using local Qwen as the PRIMARY model.

Add an API LLM only as a controlled fallback.

==================================================

1. OBJECTIVE
   ==================================================

Build:

Primary Local LLM
+
Reliability Detection
+
API LLM Fallback
+
Provider Abstraction
+
Observability

Architecture:

Agent
↓
LLM Provider Interface
├── Local Qwen1.5-1B
└── API LLM fallback
↓
Same Tool Registry
↓
Financial Engine / RAG
↓
Final Response

==================================================
2. LLM PROVIDER INTERFACE
=========================

Create a common interface:

LLMProvider

Example:

generate(
messages,
tools,
temperature,
max_tokens
)

Implement:

LocalQwenProvider
ApiLLMProvider

The Agent Service must depend on the interface, not a concrete provider.

Do NOT make AgentService directly depend on Qwen or a specific API provider.

==================================================
3. PRIMARY PROVIDER
===================

Local Qwen1.5-1B-Instruct remains the primary model.

Configuration:

LLM_PRIMARY_PROVIDER=local

LOCAL_LLM_MODEL=<configured model>
LOCAL_LLM_BASE_URL=<local inference endpoint>
LOCAL_LLM_TIMEOUT=20

Keep the exact model configurable.

Do not hard-code model names throughout the codebase.

==================================================
4. API FALLBACK
===============

Add configuration:

API_FALLBACK_ENABLED=true

API_LLM_PROVIDER=<configured provider>
API_LLM_MODEL=<configured model>
API_LLM_TIMEOUT=30

API key must come from environment configuration.

Never commit API keys.

Never print API keys in logs.

==================================================
5. FALLBACK CONDITIONS
======================

Fallback to the API model only when the local model cannot reliably process the request.

Supported reasons:

LOCAL_TIMEOUT
LOCAL_UNAVAILABLE
LOCAL_PARSE_ERROR
LOCAL_INVALID_TOOL
LOCAL_MAX_RETRIES
LOCAL_INTERNAL_ERROR

Do not fallback simply because the answer is inconvenient.

Do not send every request to the API.

Local Qwen must always be attempted first unless the circuit breaker is OPEN.

==================================================
6. MODEL OUTPUT VALIDATION
==========================

Reuse Stage 7 Pydantic validation.

Local model response must pass:

JSON parsing
schema validation
tool validation
argument validation

If local Qwen produces malformed output:

retry according to configuration.

Suggested:

MAX_LOCAL_RETRIES=2

If still invalid:

fallback to API.

Do not retry indefinitely.

==================================================
7. TOOL REGISTRY MUST BE SHARED
===============================

Both models MUST use the exact same tool registry:

get_monthly_summary
get_transactions
get_category_spending
get_recurring_payments
get_upcoming_obligations
get_budget_status
get_goal_status
analyze_purchase
search_financial_documents

Do not duplicate tools for the API model.

Do not allow either model to generate arbitrary SQL.

==================================================
8. SAME FINANCIAL ENGINE
========================

Local Qwen and API LLM must ultimately call:

existing services
existing repositories
existing financial engine
existing RAG retrieval service

The LLM provider must NEVER calculate:

income
expenses
balances
budget percentages
goal progress
purchase scenarios
anomaly scores

All financial calculations remain deterministic.

==================================================
9. FALLBACK CONTEXT
===================

When fallback occurs, send the API model the same relevant context:

system instructions
conversation summary
recent conversation messages
current user message
available tools

Do not restart the conversation.

Do not lose previous tool results when fallback happens if they are relevant.

==================================================
10. DATA MINIMIZATION
=====================

Do not send unnecessary sensitive information to the API provider.

Never send:

passwords
JWT tokens
API keys
database credentials
internal secrets

Do not send the entire transaction database.

Do not send entire uploaded documents when only retrieved chunks are needed.

For RAG:

User query
→ local retrieval
→ relevant chunks
→ API model

The API model should receive only relevant retrieved evidence.

==================================================
11. USER ISOLATION
==================

API fallback must preserve the same security model.

Never let the model specify:

user_id

The application must inject:

current_user.id

All tools must remain user-scoped.

User A must never access User B's:

transactions
budgets
goals
documents
conversation history
RAG chunks

==================================================
12. FALLBACK SERVICE
====================

Create something similar to:

app/agent/llm_router.py

Responsibilities:

select primary provider
call local provider
detect failure
retry local if appropriate
fallback to API
return provider information

Example:

route_request(...)

The Agent Service should not contain duplicated fallback logic.

==================================================
13. CIRCUIT BREAKER
===================

Implement a simple circuit breaker for local Qwen.

States:

CLOSED
OPEN
HALF_OPEN

Behavior:

CLOSED:
normal local requests.

Repeated local failures:
OPEN circuit.

OPEN:
temporarily skip local model and use API fallback.

After cooldown:
HALF_OPEN.

Send one test request.

If successful:
CLOSED.

If failed:
OPEN again.

Make configuration available:

CIRCUIT_FAILURE_THRESHOLD=3
CIRCUIT_COOLDOWN_SECONDS=30

Keep implementation simple.

Do not introduce a distributed circuit breaker.

This is a modular monolith.

==================================================
14. FALLBACK REASON
===================

Create an enum:

LOCAL_TIMEOUT
LOCAL_UNAVAILABLE
LOCAL_PARSE_ERROR
LOCAL_INVALID_TOOL
LOCAL_MAX_RETRIES
LOCAL_INTERNAL_ERROR

Every fallback must record a reason.

Example:

{
"fallback": true,
"fallback_reason": "LOCAL_TIMEOUT"
}

==================================================
15. OBSERVABILITY
=================

Record:

provider
model
latency_ms
fallback
fallback_reason
tool_count
success
error type

Use structured logs.

Do not log:

API keys
JWT tokens
passwords
entire financial documents
entire prompts unless explicitly needed for debugging

==================================================
16. MESSAGE METADATA
====================

Reuse Stage 5 message metadata.

Example:

{
"provider": "local",
"model": "Qwen1.5-1B-Instruct",
"fallback": false,
"latency_ms": 950
}

Fallback example:

{
"provider": "api",
"model": "...",
"fallback": true,
"fallback_reason": "LOCAL_TIMEOUT",
"latency_ms": 1820
}

Keep metadata compact.

==================================================
17. TOKEN / USAGE TRACKING
==========================

If the provider exposes token usage, store:

input_tokens
output_tokens

If unavailable, use null.

Do not invent token counts.

==================================================
18. ERROR HANDLING
==================

Handle:

local model unavailable
local timeout
API unavailable
API timeout
malformed local response
malformed API response
unknown tool
invalid arguments
tool failure
database failure
RAG failure

Never expose stack traces to users.

Use safe user-facing messages.

Log technical information server-side.

==================================================
19. NO FALSE FALLBACK
=====================

Do not fallback because the financial result is surprising.

Example:

If the financial engine returns:

projected_balance = -5000

that is still a valid tool result.

Do NOT ask another LLM to verify or change it.

The deterministic financial engine remains authoritative.

==================================================
20. NO MODEL-BASED CONFIDENCE DECISION
======================================

Do not trust a model-generated:

confidence = 0.95

as the main fallback criterion.

Use observable signals:

valid response
valid schema
valid tool
valid arguments
successful tool execution
timeout
provider availability

==================================================
21. TESTS
=========

Add tests for:

1. local provider success

2. API provider success

3. local timeout

4. local unavailable

5. local malformed JSON

6. local invalid tool

7. local retry

8. API fallback

9. fallback reason

10. API failure

11. circuit CLOSED

12. circuit OPEN

13. circuit HALF_OPEN

14. circuit recovery

15. shared tool registry

16. shared financial engine

17. user isolation

18. API key is never logged

19. JWT is never sent to provider

20. assistant response persistence

21. model_used

22. Stage 1 tests

23. Stage 2 tests

24. Stage 3 tests

25. Stage 4 tests

26. Stage 5 tests

27. Stage 6 tests

28. Stage 7 tests

==================================================
22. CONFIGURATION EXAMPLE
=========================

Use environment configuration similar to:

LLM_PRIMARY_PROVIDER=local

LOCAL_LLM_MODEL=Qwen1.5-1B-Instruct
LOCAL_LLM_BASE_URL=http://localhost:8000
LOCAL_LLM_TIMEOUT=20

API_FALLBACK_ENABLED=true

API_LLM_PROVIDER=<provider>
API_LLM_MODEL=<model>
API_LLM_API_KEY=<secret>
API_LLM_TIMEOUT=30

MAX_LOCAL_RETRIES=2
MAX_API_RETRIES=1

CIRCUIT_FAILURE_THRESHOLD=3
CIRCUIT_COOLDOWN_SECONDS=30

Do not commit actual secrets.

==================================================
23. EXAMPLE FLOW
================

Normal:

User
→ Agent
→ Local Qwen
→ Tool
→ Financial Engine
→ Qwen
→ Answer

Fallback:

User
→ Agent
→ Local Qwen
→ timeout
→ retry
→ timeout
→ API LLM
→ Tool
→ Financial Engine
→ API LLM
→ Answer

The user should still receive one normal assistant response.

==================================================
24. IMPORTANT MODEL SWAPPABILITY
================================

The current model is:

Qwen1.5-1B-Instruct

But future model changes must require only configuration changes wherever possible.

Do not create logic such as:

if model == "Qwen1.5-1B":
...

Avoid model-specific business logic.

The model is an implementation detail.

==================================================
25. EXPECTED STRUCTURE
======================

Adapt to the existing codebase.

Suggested:

backend/
└── app/
└── agent/
├── agent_service.py
├── llm_provider.py
├── qwen_provider.py
├── api_provider.py
├── llm_router.py
├── circuit_breaker.py
├── tool_registry.py
├── tool_executor.py
└── schemas.py

==================================================
26. DEFINITION OF DONE
======================

[ ] LLMProvider abstraction
[ ] Local Qwen provider
[ ] API provider
[ ] Local-first routing
[ ] Retry logic
[ ] Fallback logic
[ ] Fallback reason
[ ] Circuit breaker
[ ] Context preserved
[ ] Same tool registry
[ ] Same financial engine
[ ] Same RAG service
[ ] User isolation
[ ] API secret protection
[ ] Structured logging
[ ] Provider metadata
[ ] Token usage when available
[ ] Tests
[ ] Stage 1–7 tests pass

STOP after Stage 8.

Do not implement Stage 9 frontend integration.
Do not implement deployment.

Implement **Stage 7 — Local LLM + Tool-Calling Agent** for the existing FinPilot backend.

CURRENT LOCAL MODEL:

Qwen1.5-1B-Instruct.

The implementation must be model-agnostic so the model can be replaced later through configuration.

IMPORTANT:

Stages 1–6 already exist.

Do NOT redesign them.

Do NOT implement Stage 8 API fallback yet.

Do NOT implement Stage 9 frontend work.

Do NOT implement deployment work.

Do NOT use an external LLM API.

Use the local Qwen model only.

==================================================

1. MAIN OBJECTIVE
   ==================================================

Connect the persistent chat system to a local Qwen1.5-1B-Instruct model and build a controlled tool-calling agent.

Architecture:

User
→ Chat API
→ Agent Service
→ Qwen
→ Tool selection
→ Tool execution
→ Qwen explanation
→ Persistent assistant message

The LLM must NOT perform financial calculations.

Python + PostgreSQL + existing Financial Engine remain authoritative for financial data.

==================================================
2. MODEL ABSTRACTION
====================

Create:

app/agent/qwen_client.py

or an equivalent abstraction.

Expose a clean interface such as:

generate(messages, temperature, max_tokens)

The rest of the application must not depend directly on the Qwen implementation.

Configuration must contain:

LLM_PROVIDER=local
LOCAL_LLM_MODEL=<configured Qwen1.5-1B-Instruct model/path>
LOCAL_LLM_BASE_URL=<local inference endpoint if applicable>
LOCAL_LLM_TIMEOUT=<configured timeout>

Do not hard-code the model name inside business logic.

Later the model must be replaceable only through configuration.

==================================================
3. QWEN RESPONSIBILITIES
========================

Qwen is responsible for:

intent understanding
entity extraction
tool selection
tool argument extraction
natural-language explanation

Qwen is NOT responsible for:

financial calculations
SQL generation
database access
user authorization
balance calculation
budget calculation
anomaly detection
forecast calculation
purchase affordability calculation

==================================================
4. CONTROLLED TOOL CALLING
==========================

Because the current model is Qwen1.5-1B-Instruct, initially implement application-controlled structured tool calling.

Do not depend on complicated autonomous agent behavior.

Expected model output:

{
"action": "tool",
"tool": "get_monthly_summary",
"arguments": {
"month": "2026-08"
}
}

or:

{
"action": "final",
"answer": "..."
}

Validate all model output with Pydantic.

Never execute unvalidated model output.

==================================================
5. TOOL REGISTRY
================

Create:

app/agent/tool_registry.py

Register these tools:

get_monthly_summary
get_transactions
get_category_spending
get_recurring_payments
get_upcoming_obligations
get_budget_status
get_goal_status
analyze_purchase
search_financial_documents

Each tool must have:

name
description
argument schema
execution function

Keep descriptions short and clear because the local model is only 1B parameters.

==================================================
6. TOOL EXECUTOR
================

Create:

app/agent/tool_executor.py

Responsibilities:

validate requested tool
validate arguments
inject authenticated user_id
execute correct service
return structured result

The model must NEVER provide user_id.

Correct:

current_user.id
+
model arguments

Incorrect:

model-generated user_id

Never trust user-controlled or model-generated ownership identifiers.

==================================================
7. TOOL IMPLEMENTATIONS
=======================

Reuse existing Stage 4 services.

Do not duplicate financial calculations.

Examples:

get_monthly_summary
→ existing financial service

get_category_spending
→ existing financial service

get_recurring_payments
→ existing recurring service

get_upcoming_obligations
→ existing obligation logic

get_budget_status
→ existing budget engine

get_goal_status
→ existing goal engine

analyze_purchase
→ existing purchase analysis engine

search_financial_documents
→ Stage 6 retrieval service

The agent is an orchestrator, not a second financial engine.

==================================================
8. AGENT SERVICE
================

Create:

app/agent/agent_service.py

Implement:

process_message(
user_id,
conversation_id,
user_message
)

Flow:

1. Verify conversation ownership.
2. Build Stage 5 conversation context.
3. Build system prompt.
4. Include recent conversation messages.
5. Include available tool definitions.
6. Send request to local Qwen.
7. Parse response.
8. If final answer:
   return answer.
9. If tool request:
   validate tool.
10. Validate arguments.
11. Execute tool.
12. Add tool result to agent context.
13. Call Qwen again.
14. Repeat only when necessary.
15. Return final answer.
16. Persist assistant response through existing chat service.

Set a strict maximum tool-call count.

Suggested:

MAX_TOOL_CALLS=3

Never allow infinite loops.

==================================================
9. SYSTEM PROMPT
================

Use a concise system prompt appropriate for Qwen1.5-1B-Instruct:

You are FinPilot, a personal finance information assistant.

Your job is to understand the user's question and use available tools.

Rules:

1. Never invent financial data.
2. Never calculate financial totals yourself.
3. Use tools for financial information.
4. Use retrieved documents only as supporting evidence.
5. Never access another user's data.
6. Do not provide investment advice.
7. Do not claim certainty when data is incomplete.
8. After receiving tool results, explain them clearly.
9. Return structured JSON when a tool is required.
10. Keep responses concise and factual.

Do not create an unnecessarily huge system prompt.

==================================================
10. CONVERSATION CONTEXT
========================

Reuse Stage 5 context_service.

Context should contain:

conversation summary
recent messages
current user message

Do NOT send the entire conversation history to Qwen.

Use the Stage 5 recent-message limit.

The database remains the source of truth for complete conversation history.

==================================================
11. TOOL RESULT FORMAT
======================

Tool results must be structured.

Example:

{
"tool": "get_category_spending",
"success": true,
"data": {
"category": "food",
"amount": "12450.00",
"transaction_count": 23
}
}

Do not turn tool results into natural-language text before giving them to the model.

==================================================
12. FINANCIAL CALCULATION RULE
==============================

This is mandatory.

Never allow Qwen to calculate:

monthly totals
income
expenses
cash flow
budget percentages
goal progress
balances
purchase scenarios
forecast values
anomaly scores

Those values must come from existing deterministic services.

The LLM may only explain the returned values.

==================================================
13. SQL RULE
============

Never allow Qwen to generate arbitrary SQL.

Do NOT implement:

Qwen
→ SQL string
→ database

Instead:

Qwen
→ predefined tool
→ service
→ repository
→ SQL

==================================================
14. RAG TOOL
============

Implement:

search_financial_documents

Arguments:

{
"query": "...",
"top_k": 5
}

The tool must call the Stage 6 retrieval service.

The current authenticated user_id must be injected by the application.

The model must not provide user_id.

Return:

document_id
chunk_id
content
score
metadata

Do not ask the LLM to invent citations.

==================================================
15. MODEL OUTPUT VALIDATION
===========================

Create Pydantic schemas such as:

AgentToolCall
AgentFinalResponse

Tool call:

{
"action": "tool",
"tool": "...",
"arguments": {}
}

Final:

{
"action": "final",
"answer": "..."
}

Reject:

invalid JSON
unknown tools
invalid arguments
missing required fields
unexpected fields where appropriate

==================================================
16. MALFORMED MODEL OUTPUT
==========================

Qwen1.5-1B may produce malformed structured output.

Implement:

parse
→ validate
→ retry once or twice
→ safe failure

Suggested:

MAX_PARSE_RETRIES=2

Never retry indefinitely.

If parsing still fails, return a controlled assistant error.

Do not fabricate a financial answer.

==================================================
17. TEMPERATURE
===============

Use a low temperature for tool selection.

Make it configurable.

Suggested initial value:

0.1–0.3

Keep it configurable.

==================================================
18. MAX TOKENS
==============

Keep output concise.

Use a configurable max token limit appropriate for the local inference server.

Do not generate unnecessarily long reasoning.

==================================================
19. SECURITY
============

All agent requests must use the authenticated user.

Never trust:

user_id from request body
user_id from model output
conversation ownership from model output
document ownership from model output

Always derive identity from:

current_user.id

Verify:

conversation belongs to current_user

before processing.

All tools must operate inside the authenticated user's scope.

==================================================
20. CHAT INTEGRATION
====================

Replace the Stage 5 placeholder response with:

agent_service.process_message(...)

The existing message persistence architecture must remain.

Flow:

POST /conversations/{id}/messages
→ save USER message
→ agent service
→ Qwen/tool loop
→ save ASSISTANT message
→ return assistant message

Preserve the existing conversation/message models.

Set model_used for local Qwen responses.

Example:

local:qwen1.5-1b-instruct

Use the configured model identifier rather than hard-coding the exact string if possible.

==================================================
21. METADATA
============

Use existing Stage 5 message metadata JSONB for useful agent information.

Potential fields:

intent
tool_calls
latency
sources
model
error

Do not store:

passwords
JWT tokens
secrets
huge prompts
unbounded model traces

Keep metadata compact.

==================================================
22. ERROR HANDLING
==================

Handle:

Qwen unavailable
Qwen timeout
invalid model response
malformed JSON
unknown tool
invalid tool arguments
tool execution error
conversation ownership failure
retrieval failure
financial engine failure

Never expose internal stack traces to the user.

Log technical details server-side.

Return safe user-facing messages.

==================================================
23. OBSERVABILITY
=================

Add structured logging for:

request start
model latency
tool selected
tool execution latency
tool success/failure
final response latency
model name

Do not log sensitive financial document contents unnecessarily.

==================================================
24. TESTS
=========

Add tests for:

1. Qwen client

2. valid final response

3. valid tool response

4. malformed JSON

5. unknown tool

6. invalid tool arguments

7. tool execution

8. authenticated user injection

9. user isolation

10. conversation ownership

11. maximum tool calls

12. Qwen timeout

13. Qwen unavailable

14. RAG tool

15. financial tool

16. purchase analysis tool

17. assistant response persistence

18. model_used

19. Stage 1 tests

20. Stage 2 tests

21. Stage 3 tests

22. Stage 4 tests

23. Stage 5 tests

24. Stage 6 tests

==================================================
25. EXAMPLE END-TO-END FLOW
===========================

User:

"How much did I spend on food last month?"

Qwen should produce something similar to:

{
"action": "tool",
"tool": "get_category_spending",
"arguments": {
"category": "food",
"start_date": "2026-08-01",
"end_date": "2026-08-31"
}
}

Python executes the tool.

Example result:

{
"category": "food",
"amount": "12450.00",
"transaction_count": 23
}

Then Qwen generates a concise explanation.

Example:

"You spent ₹12,450 on food in August across 23 transactions."

The amount MUST come from the tool result.

==================================================
26. PURCHASE EXAMPLE
====================

User:

"Can I afford a ₹60,000 laptop?"

The agent should call:

analyze_purchase

with:

{
"amount": "60000",
"purchase_date": "..."
}

The financial engine produces the scenario.

Qwen explains the returned scenario.

Do NOT allow Qwen to independently decide affordability.

Do NOT implement a BUY/DO NOT BUY classification.

==================================================
27. EXPECTED STRUCTURE
======================

Add something similar to:

backend/
└── app/
├── agent/
│   ├── agent_service.py
│   ├── qwen_client.py
│   ├── tool_registry.py
│   ├── tool_executor.py
│   ├── prompt_builder.py
│   └── schemas.py
│
├── api/
│   └── v1/
│
├── services/
│
└── tests/
├── test_agent.py
├── test_tools.py
├── test_qwen_client.py
└── test_agent_security.py

Adapt this structure to the existing codebase.

==================================================
28. DO NOT OVERENGINEER
=======================

Do NOT add:

LangGraph unless already required
multiple autonomous agents
multi-agent communication
arbitrary SQL generation
vector database duplication
complex planning loops
long chain-of-thought storage
external LLM APIs
API fallback
frontend changes

The current objective is:

Qwen1.5-1B
+
controlled tool calling
+
existing financial engine
+
existing RAG
+
persistent chat

==================================================
29. DEFINITION OF DONE
======================

Stage 7 is complete when:

[ ] Qwen1.5-1B-Instruct connected
[ ] Model configurable through environment
[ ] Qwen client abstraction created
[ ] Agent service created
[ ] Tool registry created
[ ] Tool executor created
[ ] Pydantic tool-call validation
[ ] Monthly summary tool
[ ] Transaction tool
[ ] Category spending tool
[ ] Recurring payment tool
[ ] Upcoming obligations tool
[ ] Budget tool
[ ] Goal tool
[ ] Purchase analysis tool
[ ] RAG search tool
[ ] Maximum tool-call limit
[ ] Malformed JSON handling
[ ] Qwen timeout handling
[ ] Conversation context integrated
[ ] Assistant responses persisted
[ ] model_used stored
[ ] User isolation verified
[ ] Conversation ownership verified
[ ] Tests pass
[ ] Stage 1–6 tests pass

STOP after Stage 7.

Do not implement Stage 8.
Do not add API LLM fallback.
Do not implement frontend.
Do not deploy.

# TASK: Replace the Local LLM with Ollama Qwen2.5 1.5B

You are modifying my existing FinPilot project.

IMPORTANT:
Do NOT rebuild the project from scratch.
Do NOT change the existing architecture.
Do NOT modify the financial engine, database schema, RAG pipeline, authentication, frontend, or tool implementations unless absolutely required for LLM integration.

I want to change ONLY the local LLM implementation.

==================================================
CURRENT LOCAL MODEL
==================================================

I have Ollama installed locally.

`ollama list` shows:

qwen2.5:1.5b-instruct-q4_K_M

The exact Ollama model name is:

qwen2.5:1.5b-instruct-q4_K_M

Ollama runs locally at:

http://localhost:11434

The model should be accessed through Ollama's local API.

==================================================
FINPILOT ARCHITECTURE TO PRESERVE
==================================================

Existing architecture:

User
 ↓
Chat API
 ↓
Agent Service
 ↓
LLM Provider
 ↓
Structured tool call
 ↓
Tool Registry
 ↓
Financial Engine / RAG
 ↓
Tool result
 ↓
LLM explanation
 ↓
Persistent assistant message

The existing architecture uses an LLM provider abstraction.

Keep this abstraction.

Do NOT directly call Ollama from random files.

Use a clean provider implementation such as:

app/agent/
├── agent_service.py
├── llm_provider.py
├── ollama_provider.py
├── tool_registry.py
├── tool_executor.py
├── prompt_builder.py
└── schemas.py

Adapt the structure to the existing project if the filenames are different.

==================================================
OBJECTIVE
==================================================

Replace the current local LLM implementation with:

Ollama + Qwen2.5 1.5B Instruct Q4_K_M

The agent must communicate with Ollama through its HTTP API.

Default configuration:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct-q4_K_M

These must come from environment variables.

Do NOT hardcode the model name throughout the code.

==================================================
ENVIRONMENT CONFIGURATION
==================================================

Add/update backend environment configuration:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct-q4_K_M

If the project already has a .env configuration system, integrate with it.

Update .env.example accordingly.

Never commit real secrets.

==================================================
LLM PROVIDER
==================================================

Create or modify the Ollama provider so it implements the existing LLMProvider interface.

Conceptually:

class LLMProvider:
    def generate(
        self,
        messages,
        tools=None,
        temperature=0.1,
        max_tokens=512
    ):
        ...

Then implement:

class OllamaProvider(LLMProvider):
    ...

Use Ollama's local HTTP API.

Prefer the Ollama `/api/chat` endpoint for conversational interaction.

The request should include:

{
    "model": "qwen2.5:1.5b-instruct-q4_K_M",
    "messages": [...],
    "stream": false,
    "options": {
        "temperature": 0.1
    }
}

Do not use cloud APIs for the primary local provider.

==================================================
IMPORTANT: SMALL MODEL CONSTRAINT
==================================================

Qwen2.5 1.5B is a small local model.

Do NOT depend blindly on native Ollama tool calling.

The agent must use a controlled structured-output protocol.

The model should return either:

1. A TOOL ACTION

or

2. A FINAL ANSWER

Example tool action:

{
  "action": "tool",
  "tool": "get_monthly_summary",
  "arguments": {
    "month": "2026-08"
  }
}

Example final response:

{
  "action": "final",
  "answer": "Your total spending in August was ..."
}

The backend must parse and validate this JSON using Pydantic.

Never execute arbitrary text as a tool call.

==================================================
TOOL CALLING FLOW
==================================================

Implement:

User question
 ↓
Agent Service
 ↓
Build system prompt
 ↓
Send messages to Ollama
 ↓
Parse model JSON
 ↓
Validate with Pydantic
 ↓
If action == "tool"
        ↓
Validate tool name
        ↓
Validate arguments
        ↓
Execute registered tool
        ↓
Return tool result to agent
        ↓
Send tool result back to Ollama
        ↓
Generate final answer
       
If action == "final"
        ↓
Return final answer

Maximum tool iterations:

3

Never allow an infinite agent loop.

==================================================
TOOL SECURITY
==================================================

The LLM must NEVER control:

- user_id
- authenticated user
- database connection
- SQL
- authorization
- file paths
- arbitrary Python execution

The authenticated user must come from the existing authentication context.

For example:

current_user.id

The tool registry must remain application-controlled.

The LLM can request:

get_monthly_summary

but the backend decides:

- whether the tool exists
- whether the user is authorized
- which user data is queried
- how arguments are validated

==================================================
AVAILABLE FINPILOT TOOLS
==================================================

Preserve the existing tools.

Expected tools include:

get_monthly_summary()
get_transactions()
get_category_spending()
get_recurring_payments()
get_upcoming_obligations()
get_budget_status()
get_goal_status()
analyze_purchase()
search_financial_documents()

Do NOT rewrite their financial logic.

Do NOT move calculations into the LLM.

==================================================
FINANCIAL CALCULATIONS
==================================================

This rule is extremely important:

The LLM must NEVER calculate financial totals.

For example, if the user asks:

"How much did I spend last month?"

The model must call:

get_monthly_summary()

The financial engine calculates the actual value.

The LLM only explains the returned result.

Same rule for:

- income
- expenses
- balances
- budget percentages
- recurring payments
- anomaly scores
- forecasts
- purchase affordability
- projected balances

Never ask the LLM to perform these calculations itself.

==================================================
SYSTEM PROMPT
==================================================

Create/update the FinPilot system prompt.

Use a concise prompt suitable for Qwen2.5 1.5B.

Example:

You are FinPilot, a personal finance information assistant.

Your job is to understand the user's question and use the available application tools.

Rules:

1. Never invent financial data.
2. Never calculate financial totals yourself.
3. Use tools whenever financial data is required.
4. Never generate SQL.
5. Never choose or modify user_id.
6. Never access the database directly.
7. Use retrieved documents only as supporting evidence.
8. Do not provide investment advice.
9. Do not claim certainty when financial data is incomplete.
10. Return ONLY valid JSON.
11. Use exactly one of these actions:
   - tool
   - final

Tool format:

{
  "action": "tool",
  "tool": "TOOL_NAME",
  "arguments": {}
}

Final format:

{
  "action": "final",
  "answer": "..."
}

Do not add Markdown fences.
Do not add explanations outside the JSON.

==================================================
JSON VALIDATION
==================================================

Create strict Pydantic schemas.

Example:

ToolCall:
{
    action: Literal["tool"],
    tool: str,
    arguments: dict
}

FinalResponse:
{
    action: Literal["final"],
    answer: str
}

Create a union/root schema if appropriate.

Reject:

- malformed JSON
- unknown actions
- unknown tools
- invalid arguments

Do not execute invalid tool calls.

==================================================
MODEL RESPONSE CLEANING
==================================================

Because Qwen2.5 1.5B may sometimes return:

```text
```json
{...}

or additional whitespace/text,

implement a safe JSON extraction/normalization layer.

However:

DO NOT blindly execute arbitrary extracted content.

The final parsed object must still pass Pydantic validation.

If parsing fails:

1. Retry the same request with a stricter JSON instruction.
2. Limit retries.
3. If still invalid, return a controlled error.

Do not create infinite retries.

==================================================
OLLAMA ERROR HANDLING
==================================================

Handle:

- Ollama unavailable
- connection refused
- timeout
- model not found
- malformed response
- empty response
- invalid JSON
- invalid tool call
- maximum tool iterations

Return clean application-level errors.

Do not expose raw stack traces to users.

Log useful diagnostic information on the backend.

==================================================
HEALTH CHECK
==================================================

Add an internal/provider health check.

The backend should be able to verify:

1. Ollama is reachable.
2. The configured model exists.

Do not download models automatically from the application.

If the model is missing, provide a clear error telling the developer to run:

ollama pull qwen2.5:1.5b-instruct-q4_K_M

==================================================
TIMEOUT
==================================================

Because this is a local model, configure a reasonable HTTP timeout.

Make it configurable through environment variables.

Example:

OLLAMA_TIMEOUT=120

Do not use extremely short timeouts that would cause the 1.5B model to fail unnecessarily.

==================================================
LOGGING
==================================================

Log:

- provider used
- model name
- request duration
- tool requested
- tool execution success/failure
- parsing failures

Do NOT log:

- passwords
- JWT tokens
- API keys
- complete sensitive financial documents
- unnecessary financial information

==================================================
API PROVIDER
==================================================

Do NOT remove the existing API provider/fallback architecture if it already exists.

Keep:

LLMProvider
   ├── OllamaProvider
   └── APIProvider

The agent should depend on the interface, not a concrete provider.

If the existing project already has fallback logic, preserve it.

The local provider should now be:

OllamaProvider

with:

model = qwen2.5:1.5b-instruct-q4_K_M

Do not duplicate agent/business logic for Ollama.

==================================================
DO NOT MODIFY
==================================================

Do NOT unnecessarily modify:

- PostgreSQL schema
- authentication
- JWT implementation
- financial engine
- transaction processing
- budget calculations
- goal calculations
- purchase analysis
- RAG/pgvector implementation
- frontend
- API endpoint contracts
- tool business logic

Only make changes required to integrate Ollama.

==================================================
TESTS
==================================================

Add/update tests for:

1. Ollama provider initialization.
2. Correct model name.
3. Correct Ollama base URL.
4. Successful generation.
5. Ollama unavailable.
6. Model unavailable.
7. Invalid JSON response.
8. Valid tool call.
9. Invalid tool call.
10. Unknown tool.
11. Maximum tool iterations.
12. Final response.
13. User isolation.
14. Financial calculations remain in backend tools.

Mock Ollama HTTP responses in unit tests.

Do NOT require Ollama to be running for normal unit tests.

==================================================
MANUAL TEST
==================================================

After implementation, verify this manually.

First:

ollama list

Confirm:

qwen2.5:1.5b-instruct-q4_K_M

Then:

ollama run qwen2.5:1.5b-instruct-q4_K_M

Confirm the model works.

Then start the FinPilot backend.

Test:

"How much did I spend on food last month?"

Expected flow:

User
 ↓
Ollama Qwen2.5 1.5B
 ↓
get_category_spending
 ↓
Financial Engine
 ↓
Exact result
 ↓
Ollama
 ↓
Final explanation

The model must NOT calculate the spending itself.

Test another question:

"What subscriptions do I have?"

Expected:

Ollama
 ↓
get_recurring_payments
 ↓
Financial Engine
 ↓
Result
 ↓
Ollama
 ↓
Answer

Test:

"If I buy a laptop for ₹60,000, how will it affect my projected balance?"

Expected:

Ollama
 ↓
analyze_purchase
 ↓
Financial Engine
 ↓
Purchase scenario
 ↓
Ollama
 ↓
Explanation

Do NOT return simply:

BUY

or:

DON'T BUY

==================================================
DOCKER / WINDOWS LOCAL DEVELOPMENT
==================================================

My current development environment is Windows.

Ollama is running on the host machine.

If the backend is running directly on Windows:

http://localhost:11434

If the backend runs inside Docker on Windows, remember that:

localhost inside the container refers to the container itself.

Use the appropriate host address/configuration, such as:

host.docker.internal

when required.

Do not blindly hardcode localhost if the backend is containerized.

Make OLLAMA_BASE_URL configurable.

==================================================
DOCUMENTATION
==================================================

Update the README with:

1. Ollama installation requirement.
2. Model requirement.
3. Model pull command.
4. How to verify the model.
5. Environment variables.
6. How to start Ollama.
7. How to start FinPilot backend.
8. Troubleshooting Ollama connection errors.

Example:

ollama pull qwen2.5:1.5b-instruct-q4_K_M

Then:

ollama list

==================================================
FINAL REQUIREMENT
==================================================

After making the changes:

1. Inspect the existing project before modifying files.
2. Reuse existing abstractions.
3. Make the smallest safe set of changes.
4. Do not rewrite working code unnecessarily.
5. Run tests.
6. Run lint/type checks if already configured.
7. Verify the backend starts.
8. Verify Ollama connectivity.
9. Verify one normal chat request.
10. Verify one tool-calling request.
11. Report exactly which files were changed.
12. Report any issues that remain.

The final architecture must remain:

React
 ↓
FastAPI
 ↓
Agent Service
 ↓
LLMProvider
 ↓
OllamaProvider
 ↓
Qwen2.5 1.5B
 ↓
Structured JSON action
 ↓
Tool Registry
 ↓
Financial Engine / RAG
 ↓
Tool Result
 ↓
Qwen2.5
 ↓
Final Answer

The key goal is:

CHANGE THE LOCAL LLM IMPLEMENTATION TO OLLAMA + QWEN2.5 1.5B WITHOUT BREAKING THE EXISTING FINPILOT ARCHITECTURE.
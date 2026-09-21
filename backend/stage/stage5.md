We are continuing development of the FinPilot personal finance application.

Completed stages:

STAGE 1 — Project Foundation
STAGE 2 — Database + Authentication
STAGE 3 — Financial Data Ingestion
STAGE 4 — Financial Intelligence Engine

Now implement ONLY:

STAGE 5 — CHAT + PERSISTENT CONVERSATION HISTORY

Do not implement RAG, embeddings, LLMs, agents, tool calling, or API LLM fallback yet.

==================================================
PROJECT CONTEXT
==================================================

FinPilot is a personal finance decision-support application.

It already has:

- authentication
- PostgreSQL
- financial documents
- transactions
- financial intelligence
- budgets
- goals
- recurring payments
- purchase scenario analysis

Stage 5 adds persistent conversational infrastructure.

The future system will allow a user to ask:

"How much did I spend on food?"

"What subscriptions do I have?"

"How much can I allocate toward my laptop?"

"How did my spending change this month?"

However, Stage 5 MUST NOT answer these questions using an LLM yet.

The chat infrastructure must be implemented independently of the future AI agent.

==================================================
CORE PRINCIPLE
==================================================

Chat persistence and AI reasoning are separate concerns.

Stage 5:

Chat storage
+
Conversation management
+
Context management

Stage 7:

LLM
+
Agent
+
Tool calling

Do not mix these responsibilities.

==================================================
DATABASE MODELS
==================================================

Create:

Conversation
Message
ConversationSummary

--------------------------------------------------
CONVERSATION
--------------------------------------------------

Fields:

id:
    UUID primary key

user_id:
    UUID foreign key users.id
    indexed
    not null

title:
    nullable string

archived:
    boolean
    default false

created_at:
    timestamp with timezone

updated_at:
    timestamp with timezone

A conversation belongs to exactly one user.

--------------------------------------------------
MESSAGE
--------------------------------------------------

Fields:

id:
    UUID primary key

conversation_id:
    UUID foreign key conversations.id
    indexed
    not null

role:
    string

Allowed:

USER
ASSISTANT
SYSTEM
TOOL

content:
    text

sequence_number:
    integer

created_at:
    timestamp with timezone

model_used:
    nullable string

metadata:
    nullable JSONB

Important:

sequence_number must preserve message ordering.

Do not rely only on timestamps for ordering.

--------------------------------------------------
CONVERSATION SUMMARY
--------------------------------------------------

Fields:

id:
    UUID primary key

conversation_id:
    UUID foreign key conversations.id
    unique
    not null

summary:
    text

message_count:
    integer

updated_at:
    timestamp with timezone

The summary represents older conversation context.

==================================================
ALEMBIC
==================================================

Create migration for:

conversations
messages
conversation_summaries

Do not use:

Base.metadata.create_all()

Use Alembic.

==================================================
RELATIONSHIPS
==================================================

User:

User
 └── conversations

Conversation:

Conversation
 ├── messages
 └── summary

Use SQLAlchemy relationships where useful.

Use cascade behavior carefully.

Deleting a conversation should not leave orphan messages or summaries.

==================================================
REPOSITORIES
==================================================

Create:

conversation_repository.py

message_repository.py

Responsibilities:

Conversation repository:

create_conversation()
get_conversation()
list_conversations()
archive_conversation()
delete_conversation()

Message repository:

create_message()
get_messages()
get_recent_messages()
count_messages()

Every repository operation involving a user's data must enforce user ownership.

==================================================
USER ISOLATION
==================================================

This is critical.

Never trust a user_id supplied by the frontend.

Always derive ownership from:

current_user.id

For example:

GET /api/v1/conversations/{conversation_id}

must effectively enforce:

conversation.id = requested_id
AND conversation.user_id = current_user.id

The same rule applies to:

messages
summaries
conversation deletion
conversation archiving

User A must never access User B's conversation.

==================================================
SCHEMAS
==================================================

Create:

ConversationCreate

ConversationResponse

ConversationListResponse

MessageCreate

MessageResponse

MessageListResponse

ConversationSummaryResponse

Do not expose internal database objects directly.

==================================================
CONVERSATION API
==================================================

Create:

POST /api/v1/conversations

Request:

{
    "title": "Monthly spending"
}

Title may be optional.

Response:

{
    "id": "...",
    "title": "Monthly spending",
    "archived": false,
    "created_at": "...",
    "updated_at": "..."
}

--------------------------------------------------

GET /api/v1/conversations

Return the authenticated user's conversations.

Support:

archived=false

Optional pagination:

limit
offset

Example:

GET /api/v1/conversations?limit=20&offset=0

Return:

{
    "items": [],
    "total": 10,
    "limit": 20,
    "offset": 0
}

Order by:

updated_at DESC

This allows the frontend to show the most recently used conversations first.

--------------------------------------------------

GET /api/v1/conversations/{conversation_id}

Return conversation metadata.

Must enforce user ownership.

--------------------------------------------------

PATCH /api/v1/conversations/{conversation_id}

Allow:

title
archived

Do not allow:

user_id
created_at
other ownership fields

--------------------------------------------------

DELETE /api/v1/conversations/{conversation_id}

Delete/archive according to implementation.

If hard deleting:

delete messages and summary safely.

Return:

{
    "message": "Conversation deleted"
}

==================================================
MESSAGE API
==================================================

Create:

GET /api/v1/conversations/{conversation_id}/messages

Parameters:

limit
offset

Return messages ordered by:

sequence_number ASC

or provide a clear pagination strategy that preserves chronological order.

--------------------------------------------------

POST /api/v1/conversations/{conversation_id}/messages

Request:

{
    "content": "How much did I spend this month?"
}

Require authentication.

Verify conversation belongs to current user.

Create USER message.

For Stage 5, create a placeholder ASSISTANT response.

Example:

{
    "message_id": "...",
    "conversation_id": "...",
    "role": "ASSISTANT",
    "content": "Your financial assistant is being initialized. The AI agent will be connected in a later stage.",
    "model_used": null
}

IMPORTANT:

Do not call any LLM.

The placeholder exists only to verify the chat infrastructure.

==================================================
MESSAGE SEQUENCE
==================================================

Every conversation must have ordered messages.

For a new conversation:

first user message:

sequence_number = 1

assistant:

sequence_number = 2

next user:

sequence_number = 3

etc.

Avoid race conditions.

If multiple messages could be submitted concurrently, use a safe database strategy.

Do not simply:

SELECT MAX(sequence_number) + 1

without considering concurrent requests.

For the initial implementation, use a transaction/locking strategy or another safe method.

==================================================
CHAT SERVICE
==================================================

Create:

app/services/chat_service.py

Responsibilities:

create_conversation()
get_conversation()
list_conversations()
add_user_message()
generate_placeholder_response()
get_message_history()
build_context()

Keep route handlers thin.

Do not put database logic directly in API routes.

==================================================
CONTEXT MANAGEMENT
==================================================

This is a critical part of Stage 5.

Do NOT send every historical message to a future LLM.

Implement a context builder abstraction.

Create something like:

app/services/context_service.py

Function:

build_conversation_context()

It should return:

{
    "summary": "...",
    "recent_messages": [...],
    "message_count": 120
}

For example:

summary:
    older conversation information

recent_messages:
    last N messages

Use a configurable:

CHAT_CONTEXT_MESSAGE_LIMIT

Default:

20

This does not mean the database only stores 20 messages.

The database stores ALL messages.

Only recent messages are selected for future LLM context.

==================================================
CONVERSATION SUMMARY
==================================================

Stage 5 should implement summary infrastructure.

Do NOT use an LLM to generate the summary yet.

Create:

ConversationSummary

and service functions:

get_summary()
save_summary()

For now the summary can be:

null/empty

or a deterministic placeholder.

Example:

"Conversation contains 100 messages."

The important requirement is that Stage 7 can later replace the summary generator with an LLM-based summarizer.

==================================================
SUMMARY STRATEGY
==================================================

Future strategy:

Recent messages:
    last 20

Older messages:
    compressed into summary

Example:

500 total messages

LLM context:

conversation summary
+
last 20 messages
+
current financial context
+
current user query

Do NOT send all 500 messages.

==================================================
CHAT CONTEXT API
==================================================

Create an internal service method:

build_context(conversation_id, user_id)

Return:

{
    "conversation_id": "...",
    "summary": "...",
    "recent_messages": [
        {
            "role": "USER",
            "content": "..."
        },
        {
            "role": "ASSISTANT",
            "content": "..."
        }
    ],
    "message_count": 42
}

This is an internal service response.

Do not expose unnecessary internal context metadata to the frontend.

==================================================
MESSAGE METADATA
==================================================

Use JSONB metadata for future extensibility.

Possible future fields:

tool_calls
sources
latency
confidence
intent
tokens
error
agent_trace_id

Stage 5 does not need to populate these.

Do not put large blobs into metadata.

==================================================
MODEL USED
==================================================

model_used should be nullable.

Stage 5:

model_used = null

Later:

local model:

"local:..."

API fallback:

"api:..."

This allows observability later.

==================================================
CHAT TITLES
==================================================

Support optional title at conversation creation.

If no title is supplied:

title = null

Do NOT use an LLM to automatically generate titles yet.

Later the frontend/agent can generate titles.

==================================================
ERROR HANDLING
==================================================

Return:

404 if conversation does not belong to user or does not exist.

Do not reveal whether another user's conversation exists.

For example:

User A requests User B conversation ID.

Return:

404 Not Found

not:

"You don't own this conversation."

==================================================
PAGINATION
==================================================

Implement pagination for:

conversations
messages

Use:

limit
offset

Validate:

limit > 0
limit <= reasonable maximum

Example maximum:

100

Do not allow:

limit=1000000

==================================================
SORTING
==================================================

Conversation list:

updated_at DESC

Message history:

sequence_number ASC

Recent messages for context:

sequence_number DESC in query,
then reverse in service if necessary.

Make the final context chronological.

==================================================
CONVERSATION UPDATED_AT
==================================================

When a message is added:

conversation.updated_at

must update.

This ensures recently active conversations appear first.

==================================================
API RESPONSE EXAMPLE
==================================================

GET:

/api/v1/conversations/{id}/messages

Response:

{
    "items": [
        {
            "id": "...",
            "role": "USER",
            "content": "How much did I spend?",
            "sequence_number": 1,
            "created_at": "..."
        },
        {
            "id": "...",
            "role": "ASSISTANT",
            "content": "The AI assistant will be connected soon.",
            "sequence_number": 2,
            "created_at": "..."
        }
    ],
    "total": 2,
    "limit": 50,
    "offset": 0
}

==================================================
FUTURE AGENT CONTRACT
==================================================

Design chat_service so Stage 7 can replace:

generate_placeholder_response()

with:

agent_service.process_message()

without redesigning the API.

Desired future flow:

POST message
        ↓
Chat Service
        ↓
Agent Service
        ↓
Tool Router
        ↓
Financial Engine / RAG
        ↓
LLM
        ↓
Assistant Message
        ↓
PostgreSQL

Stage 5 must create the seam for this integration.

==================================================
OPTIONAL STREAMING PREPARATION
==================================================

Do not implement WebSockets.

Do not implement actual token streaming yet.

However, keep the architecture compatible with future SSE.

Future endpoint may be:

POST /api/v1/conversations/{id}/messages/stream

For now normal HTTP JSON is sufficient.

==================================================
SECURITY
==================================================

All chat APIs require authentication.

Every query must be user-scoped.

Never allow:

conversation_id + arbitrary user_id

to bypass ownership.

Do not store passwords, tokens or secrets in message metadata.

==================================================
TESTING
==================================================

Create tests for:

1. Create conversation.

2. List conversations.

3. Get conversation.

4. Update conversation title.

5. Archive conversation.

6. Delete conversation.

7. Create user message.

8. Create placeholder assistant message.

9. Message ordering.

10. Message pagination.

11. Conversation pagination.

12. Conversation updated_at changes after message.

13. Context builder returns recent messages.

14. Context builder returns messages in chronological order.

15. Summary retrieval.

16. User A cannot access User B conversation.

17. User A cannot access User B messages.

18. User A cannot delete User B conversation.

19. User A cannot modify User B conversation.

20. Empty conversation.

21. Invalid conversation ID.

22. Invalid pagination values.

23. Very long message handling.

24. Stage 1 tests still pass.

25. Stage 2 tests still pass.

26. Stage 3 tests still pass.

27. Stage 4 tests still pass.

==================================================
MESSAGE SIZE
==================================================

Set a reasonable maximum message length.

Example:

16,000 characters.

Reject excessively large messages.

This protects the backend and future LLM context.

==================================================
DATABASE INDEXES
==================================================

Create indexes for:

conversations.user_id
conversations.updated_at

messages.conversation_id
messages.sequence_number

conversation_summaries.conversation_id

Consider composite indexes where appropriate.

==================================================
ALEMBIC
==================================================

Create migration for:

conversations
messages
conversation_summaries

Do not modify previous migrations destructively.

==================================================
README
==================================================

Update README with:

- chat architecture
- database models
- conversation lifecycle
- message lifecycle
- context management
- API examples
- testing instructions

Explain:

Database stores complete history.

LLM context uses:

summary + recent messages + current context.

==================================================
NO AI
==================================================

Do not import:

OpenAI
Gemini
Ollama
LangChain
LlamaIndex
Transformers

No LLM calls.

No RAG.

No embeddings.

No agent framework.

==================================================
FINAL VERIFICATION
==================================================

After implementation:

1. Show final directory tree.

2. Show database models.

3. Show Alembic migration.

4. Create a conversation.

5. Add a user message.

6. Verify placeholder assistant response.

7. Retrieve conversation history.

8. Verify pagination.

9. Verify context builder.

10. Verify summary infrastructure.

11. Verify user isolation.

12. Run all tests.

13. Confirm Stage 1, 2, 3 and 4 tests still pass.

14. Report limitations.
15. do not hardcode anything

STOP AFTER STAGE 5.
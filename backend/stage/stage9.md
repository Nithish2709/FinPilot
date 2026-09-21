Implement **Stage 9 — Frontend Integration** for FinPilot.

IMPORTANT:

Stages 1–8 are already implemented.

The backend is FastAPI.

The frontend is React + Vite.

Do not redesign the backend.

Do not modify financial calculations.

Do not modify the agent architecture unless a small API integration change is required.

The local primary model remains Qwen1.5-1B-Instruct with API fallback from Stage 8.

==================================================

1. OBJECTIVE
   ==================================================

Connect the React/Vite frontend to the existing FastAPI backend.

Build a functional FinPilot UI for:

Authentication
Dashboard
Chat
Document upload
Budgets
Goals
Purchase analysis

The frontend should consume backend APIs and display backend results.

Do not duplicate financial calculations in React.

==================================================
2. FRONTEND STRUCTURE
=====================

Use a clean structure similar to:

src/
├── api/
│   ├── client.ts
│   ├── auth.ts
│   ├── dashboard.ts
│   ├── chat.ts
│   ├── documents.ts
│   ├── budgets.ts
│   ├── goals.ts
│   └── purchases.ts
│
├── components/
│   ├── layout/
│   ├── dashboard/
│   ├── chat/
│   ├── documents/
│   ├── budgets/
│   ├── goals/
│   └── purchases/
│
├── pages/
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   ├── Chat.tsx
│   ├── Documents.tsx
│   ├── Budgets.tsx
│   ├── Goals.tsx
│   └── PurchaseAnalysis.tsx
│
├── hooks/
├── types/
└── utils/

Adapt to the existing frontend if files already exist.

==================================================
3. API CLIENT
=============

Create a centralized API client.

Use:

VITE_API_BASE_URL

Example:

VITE_API_BASE_URL=http://localhost:8000/api/v1

Do not hard-code API URLs throughout React components.

All API modules must use the central client.

==================================================
4. AUTHENTICATION
=================

Implement:

Register
Login
Logout
Current user

Backend:

POST /auth/register
POST /auth/login
POST /auth/refresh
GET /auth/me

After login:

store authentication state securely according to the existing backend token architecture.

Every protected API request must include:

Authorization: Bearer <token>

Do not expose tokens in URLs.

Handle expired authentication cleanly.

A 401 should redirect the user to login when appropriate.

==================================================
5. DASHBOARD
============

Connect:

GET /dashboard

Display:

monthly income
monthly expenses
net cash flow
category spending
upcoming obligations
budget information
goal information
unusual spending if available

Use charts where useful.

Recommended:

Recharts

Do NOT recalculate financial values in the frontend.

Backend values are authoritative.

==================================================
6. CHAT
=======

Build the primary FinPilot chat interface.

Support:

conversation list
create conversation
select conversation
load messages
send message
display assistant response
loading state
errors

Backend:

POST /conversations
GET /conversations
GET /conversations/{id}
GET /conversations/{id}/messages
POST /conversations/{id}/messages

Message flow:

User enters message
→ POST message
→ show loading state
→ receive assistant response
→ append response
→ refresh conversation metadata

Do not expose model chain-of-thought.

Safe status messages are allowed:

"Analyzing your financial data..."
"Retrieving relevant information..."

==================================================
7. CHAT SOURCES
===============

If assistant response contains source information:

Display a compact source section.

Example:

Sources

statement_august.pdf · Page 4

Do not expose internal database IDs unless necessary.

==================================================
8. CHAT ERROR HANDLING
======================

Handle:

401
403
404
422
429
500
503
timeout

Show user-friendly errors.

Do not expose backend stack traces.

==================================================
9. DOCUMENT UPLOAD
==================

Build a document upload page.

Supported types should match backend support.

At minimum:

PDF
CSV
TXT

Flow:

select file
→ upload
→ show PROCESSING
→ poll/refresh status if backend supports status
→ show COMPLETED or FAILED

Display:

filename
status
upload date

Do not claim processing completed until backend confirms it.

==================================================
10. DOCUMENT SEARCH
===================

If exposing document search directly, use:

POST /documents/search

Request:

{
"query": "...",
"top_k": 5
}

Display relevant source snippets.

Do not calculate financial values from retrieved chunks.

==================================================
11. BUDGETS
===========

Build budget management.

Support:

create
list
view
update
delete

Backend:

POST /budgets
GET /budgets
GET /budgets/{id}
PUT /budgets/{id}
DELETE /budgets/{id}

Display:

budget amount
current spending
status

Status must come from backend.

Do not independently determine:

ON_TRACK
NEAR_LIMIT
OVER_BUDGET

==================================================
12. GOALS
=========

Build goal management.

Support:

create
list
view
update
delete

Display:

goal name
target amount
current amount
progress
target date
required monthly saving

Do not recalculate authoritative goal values in React.

==================================================
13. PURCHASE ANALYSIS
=====================

Build a dedicated purchase analysis UI.

Input:

description
amount
purchase date

Backend:

POST /purchases/analyze

Display:

current balance
upcoming obligations
purchase amount
projected balance
safety buffer
buffer difference
purchase-now scenario
wait scenario

Do not display a simplistic:

BUY
DO NOT BUY

decision.

Display the financial scenario and supporting values.

==================================================
14. RESPONSIVE DESIGN
=====================

The application should work on:

desktop
tablet
mobile

Use responsive layout.

Keep the navigation simple.

Suggested desktop:

sidebar + main content

Mobile:

collapsible navigation

==================================================
15. LOADING STATES
==================

Every asynchronous page must have a loading state.

Examples:

Dashboard:
"Loading financial summary..."

Chat:
"FinPilot is analyzing..."

Upload:
"Processing document..."

Purchase:
"Analyzing scenario..."

Avoid blank screens.

==================================================
16. EMPTY STATES
================

Handle users with no data.

Examples:

No transactions:

"No financial transactions have been imported yet."

No goals:

"Create your first financial goal."

No conversations:

"Start a conversation with FinPilot."

Do not show broken charts when data is empty.

==================================================
17. TYPESCRIPT TYPES
====================

Create types matching backend schemas.

For example:

Transaction
DashboardSummary
Budget
Goal
Conversation
Message
Document
PurchaseAnalysis
Source

Do not use `any` everywhere.

Keep frontend types aligned with backend response schemas.

==================================================
18. SECURITY
============

Do not:

hard-code API keys
hard-code database credentials
expose secrets
send user_id manually when backend derives it from JWT

Frontend should never control authorization scope.

==================================================
19. PERFORMANCE
===============

Avoid unnecessary API requests.

Use:

pagination
reasonable caching
request cancellation where useful

Do not repeatedly reload the entire dashboard after every small action if a targeted refresh is possible.

==================================================
20. ACCESSIBILITY
=================

Use:

semantic buttons
labels
keyboard-accessible controls
visible focus states
proper form validation
meaningful error messages

Charts should have accessible labels or summaries where practical.

==================================================
21. API ERROR NORMALIZATION
===========================

Centralize API errors.

Example:

ApiError {
status
message
code
}

Components should not each implement their own raw HTTP error parsing.

==================================================
22. DEFINITION OF DONE
======================

[ ] React connected to FastAPI
[ ] Environment-based API URL
[ ] Register
[ ] Login
[ ] Logout
[ ] Authenticated API requests
[ ] Dashboard
[ ] Financial charts
[ ] Conversation list
[ ] Chat interface
[ ] Message persistence visible
[ ] Assistant loading state
[ ] Source display
[ ] Document upload
[ ] Document status
[ ] Budget UI
[ ] Goal UI
[ ] Purchase analysis UI
[ ] Empty states
[ ] Error states
[ ] Responsive design
[ ] TypeScript types
[ ] No frontend financial recalculation
[ ] No secrets in frontend
[ ] Existing backend tests still pass
[ ] Frontend build succeeds

STOP after Stage 9.

Do not implement Stage 10 deployment/security hardening yet.

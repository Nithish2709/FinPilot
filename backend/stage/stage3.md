We are continuing development of the FinPilot personal finance application.

STAGE 1: Project Foundation
STAGE 2: Database + Authentication

are already implemented.

Now implement ONLY:

STAGE 3 — FINANCIAL DATA INGESTION

Do not implement Stage 4 financial intelligence, RAG, LLM, agents, budgets, goals, forecasting, or purchase analysis.

==================================================
PROJECT CONTEXT
==================================================

FinPilot is a personal finance decision-support application.

The system will eventually allow users to:

- upload financial statements
- analyze transactions
- categorize spending
- detect recurring payments
- detect unusual spending
- calculate monthly summaries
- track budgets
- track financial goals
- identify upcoming obligations
- ask natural-language questions
- retrieve evidence from uploaded financial documents
- use a local LLM for language understanding
- use an API LLM as fallback

Architecture principle:

SQL/PostgreSQL:
    structured financial facts

Python:
    financial calculations and deterministic rules

RAG:
    unstructured document evidence

LLM:
    language understanding, extraction, routing and explanation

Never use an LLM to calculate transaction totals.

==================================================
STAGE 3 GOAL
==================================================

Implement a reliable financial data ingestion pipeline:

FILE
 ↓
UPLOAD
 ↓
VALIDATION
 ↓
EXTRACTION
 ↓
NORMALIZATION
 ↓
VALIDATION
 ↓
DEDUPLICATION
 ↓
DATABASE
 ↓
IMPORT SUMMARY

Supported input formats:

1. CSV
2. Excel XLSX
3. PDF

==================================================
DATABASE MODELS
==================================================

Create:

Account
Transaction
Document

Do not create future models such as:

Budget
Goal
Conversation
Message
RecurringPayment

Those belong to later stages.

--------------------------------------------------
ACCOUNT
--------------------------------------------------

Create Account model:

id:
    UUID primary key

user_id:
    UUID foreign key users.id
    indexed
    not null

name:
    string
    not null

account_type:
    string

currency:
    string
    default "INR"

is_active:
    boolean
    default true

created_at:
    timestamp with timezone

updated_at:
    timestamp with timezone

A user can have multiple accounts.

Examples:

Savings Account
Current Account
Credit Card
Wallet

Every account belongs to exactly one user.

--------------------------------------------------
DOCUMENT
--------------------------------------------------

Create Document model:

id:
    UUID primary key

user_id:
    UUID foreign key users.id
    indexed
    not null

filename:
    string
    not null

mime_type:
    string

file_size:
    integer

storage_key:
    string

status:
    enum/string

Possible status values:

UPLOADED
PROCESSING
COMPLETED
FAILED

total_records:
    integer
    default 0

successful_records:
    integer
    default 0

failed_records:
    integer
    default 0

created_at:
    timestamp with timezone

updated_at:
    timestamp with timezone

error_message:
    nullable string

IMPORTANT:

For Stage 3 use local file storage for development if necessary.

Design the Document model so object storage can be introduced later.

Do not implement cloud object storage unless required.

--------------------------------------------------
TRANSACTION
--------------------------------------------------

Create Transaction model:

id:
    UUID primary key

user_id:
    UUID foreign key users.id
    indexed
    not null

account_id:
    UUID foreign key accounts.id
    indexed
    nullable initially if account cannot be determined

source_document_id:
    UUID foreign key documents.id
    indexed
    nullable

transaction_date:
    date
    not null

merchant:
    nullable string

description:
    string
    not null

amount:
    DECIMAL
    not null

currency:
    string
    default "INR"

transaction_type:
    string
    not null

Possible values:

DEBIT
CREDIT
REFUND
TRANSFER
UNKNOWN

category:
    nullable string

subcategory:
    nullable string

is_recurring:
    boolean
    default false

confidence:
    nullable DECIMAL

external_reference:
    nullable string

is_duplicate:
    boolean
    default false

is_valid:
    boolean
    default true

validation_error:
    nullable string

created_at:
    timestamp with timezone

updated_at:
    timestamp with timezone

Use Decimal/Numeric for amount.

Do not use float.

==================================================
DATABASE CONSTRAINTS
==================================================

Every Account, Document and Transaction must belong to a user.

Do not trust user_id from the frontend.

Use the authenticated user from:

get_current_user()

For example:

current_user.id

must determine ownership.

Never allow:

request.user_id

to determine ownership.

This is critical for financial data isolation.

==================================================
ALEMBIC
==================================================

Create Alembic migrations for:

accounts
documents
transactions

Do not use:

Base.metadata.create_all()

Alembic must remain the source of truth for database schema.

==================================================
FILE UPLOAD API
==================================================

Create:

POST /api/v1/documents/upload

Require authentication.

Accept:

multipart/form-data

Field:

file

Supported:

.csv
.xlsx
.pdf

Reject unsupported formats.

Set reasonable maximum file size.

Do not allow arbitrary executable files.

Return immediately after creating the Document record if processing is asynchronous.

For the initial implementation, processing may be performed synchronously if necessary for simplicity, but structure the code so it can later move to a background worker.

Response should contain:

{
    "document_id": "...",
    "filename": "...",
    "status": "PROCESSING"
}

or:

{
    "document_id": "...",
    "filename": "...",
    "status": "COMPLETED",
    "total_records": 100,
    "successful_records": 97,
    "failed_records": 3
}

==================================================
DOCUMENT STATUS API
==================================================

Create:

GET /api/v1/documents/{document_id}

Require authentication.

Return document information.

IMPORTANT:

A user must only be able to retrieve their own document.

Query using authenticated user ID.

For example:

WHERE document.id = document_id
AND document.user_id = current_user.id

Never query only by document_id.

==================================================
TRANSACTION API
==================================================

Create:

GET /api/v1/transactions

Require authentication.

Support basic filters:

start_date
end_date
category
transaction_type
account_id
limit
offset

Example:

GET /api/v1/transactions?start_date=2026-09-01&end_date=2026-09-30

Always filter by authenticated user.

Return paginated results.

Response:

{
    "items": [...],
    "total": 100,
    "limit": 50,
    "offset": 0
}

Do not implement advanced analytics yet.

==================================================
PARSING ARCHITECTURE
==================================================

Create a clean parser architecture.

Suggested:

app/services/ingestion/

    __init__.py
    ingestion_service.py
    validators.py
    normalizer.py

    parsers/
        __init__.py
        base.py
        csv_parser.py
        excel_parser.py
        pdf_parser.py

The parser should produce a common intermediate structure.

For example:

NormalizedTransaction:

{
    "transaction_date": date,
    "merchant": "...",
    "description": "...",
    "amount": Decimal("1000.00"),
    "currency": "INR",
    "transaction_type": "DEBIT",
    "external_reference": null
}

The database layer should not care whether the original file was CSV, Excel or PDF.

==================================================
CSV PARSER
==================================================

Implement CSV parsing using pandas.

Handle common column names such as:

Date
Transaction Date
Txn Date

Description
Narration
Details

Merchant

Debit
Withdrawal

Credit
Deposit

Amount

Do not assume every CSV uses the same column names.

Implement a column mapping/normalization layer.

Example:

"Txn Date"
→ transaction_date

"Withdrawal"
→ debit

"Deposit"
→ credit

If debit and credit columns exist:

Debit:
    amount = negative/DEBIT representation

Credit:
    amount = positive/CREDIT representation

However, preserve transaction_type explicitly.

Do not depend only on the sign.

==================================================
EXCEL PARSER
==================================================

Use pandas/openpyxl.

Support .xlsx.

Use the same normalization pipeline as CSV.

Do not duplicate business logic between CSV and Excel.

Both should eventually produce:

NormalizedTransaction

==================================================
PDF PARSER
==================================================

Use PyMuPDF.

Extract text from PDF.

Attempt to identify transaction rows.

Handle common statement formats.

Important:

PDF extraction may be imperfect.

Never silently convert a missing amount into zero.

If an amount cannot be confidently extracted:

mark the row invalid

and provide:

validation_error

Do not fabricate financial values.

If the PDF has no extractable text:

mark the document as FAILED or indicate that OCR is required.

Do not implement OCR in this stage unless necessary.

==================================================
NORMALIZATION
==================================================

Create a normalization service.

Normalize:

dates
amounts
currency
transaction type
merchant
description

Dates should become:

Python date

Amounts should become:

Decimal

Transaction types should become:

DEBIT
CREDIT
REFUND
TRANSFER
UNKNOWN

Trim unnecessary whitespace.

Normalize common date formats.

Handle commas in amounts:

"₹1,25,000.50"

should become:

Decimal("125000.50")

Do not lose decimal precision.

==================================================
TRANSACTION VALIDATION
==================================================

Validate every normalized transaction.

Required:

transaction_date
description
amount
transaction_type

Invalid records should not crash the entire import.

Instead:

is_valid = false

validation_error = "..."

Continue processing other records.

Import summary must show:

total_records
successful_records
failed_records

==================================================
DUPLICATE DETECTION
==================================================

Implement deterministic duplicate detection.

A possible duplicate fingerprint can use:

user_id
transaction_date
amount
merchant
description
account_id
external_reference

Do not rely only on UUID.

If an identical transaction already exists from the same source document/import:

mark it as duplicate or skip insertion according to the chosen strategy.

Document the strategy clearly.

Do not delete legitimate repeated transactions simply because they have the same amount.

Example:

Two monthly Netflix payments of ₹649 are NOT automatically duplicates.

Duplicate detection must consider multiple fields.

==================================================
REFUNDS AND CREDITS
==================================================

Do not confuse:

refund
credit
debit

For example:

Purchase:
    DEBIT
    1000

Refund:
    REFUND
    1000

Both records must be preserved.

Do not overwrite the original purchase.

==================================================
FAILED / CANCELLED DATA
==================================================

If the source explicitly identifies:

cancelled
failed
reversed

do not blindly treat it as a completed expense.

Mark or exclude such records according to transaction status.

Do not invent a completed transaction from failed data.

==================================================
INCOMPLETE DATA COVERAGE
==================================================

Track import quality.

The ingestion result should expose:

total_records
successful_records
failed_records

Optionally:

duplicate_records

This will later allow the dashboard/agent to explain:

"Your uploaded statement contains 97 valid transactions and 3 rows that could not be parsed."

Do not claim the financial picture is complete when data coverage is incomplete.

==================================================
IMPORT RESULT
==================================================

Create a structured import result:

{
    "document_id": "...",
    "total_records": 100,
    "successful_records": 95,
    "failed_records": 3,
    "duplicate_records": 2,
    "status": "COMPLETED"
}

For failures, retain useful validation information.

Do not expose internal stack traces to users.

==================================================
FILE STORAGE
==================================================

For development:

store uploaded files under a controlled local directory such as:

storage/uploads/

Generate safe unique storage keys.

Do not use the original filename as the filesystem path.

Prevent path traversal.

Example:

../../malicious.exe

must never escape the upload directory.

The database should store:

storage_key

rather than relying on arbitrary user-provided paths.

==================================================
SECURITY
==================================================

Implement:

- authenticated uploads
- allowed file extensions
- MIME/content validation where practical
- file size limit
- safe filenames/storage keys
- user ownership checks
- no arbitrary file execution
- no user-controlled SQL
- parameterized/ORM queries
- no sensitive data in logs

Most importantly:

Every query involving financial data must be scoped to:

current_user.id

==================================================
CATEGORIZATION
==================================================

Do NOT implement an LLM categorization system yet.

For Stage 3:

leave:

category = null
subcategory = null

unless a deterministic basic rule is implemented.

Stage 4 will implement the financial intelligence/categorization layer.

Do not add an LLM just for categorization in this stage.

==================================================
SERVICE STRUCTURE
==================================================

Use separation:

API:
    handles HTTP

Ingestion service:
    orchestrates file processing

Parser:
    extracts raw transaction information

Normalizer:
    converts raw information into common schema

Validator:
    validates normalized transactions

Repository:
    database operations

Model:
    SQLAlchemy database representation

Do not place the entire pipeline inside upload.py/auth.py.

==================================================
TEST DATA
==================================================

Create small test fixtures:

tests/fixtures/

Include:

sample_transactions.csv
sample_transactions.xlsx
sample_statement.pdf

If creating a PDF fixture is difficult, create a minimal text-based test PDF or mock the parser in unit tests.

CSV fixture should contain examples of:

DEBIT
CREDIT
REFUND
duplicate row
invalid amount
missing description

==================================================
TESTING
==================================================

Create tests for:

1. CSV parsing.

2. Excel parsing.

3. PDF extraction.

4. Date normalization.

5. Amount normalization.

6. Decimal precision.

7. Transaction type detection.

8. Invalid rows.

9. Duplicate detection.

10. Refund handling.

11. File extension validation.

12. File size validation.

13. Unauthorized document upload.

14. User A cannot access User B's document.

15. User A cannot retrieve User B's transactions.

16. Pagination.

17. Import summary.

18. Stage 1 health endpoint still works.

19. Stage 2 authentication tests still work.

Use an isolated test database.

Never run destructive tests against the real development database.

==================================================
API DESIGN
==================================================

Implement:

POST /api/v1/documents/upload

GET /api/v1/documents/{document_id}

GET /api/v1/transactions

Do not implement:

GET /dashboard

GET /subscriptions

GET /budgets

GET /goals

POST /purchases/analyze

Those belong to later stages.

==================================================
PERFORMANCE
==================================================

Do not load unnecessarily huge files entirely into memory if avoidable.

For the initial MVP, reasonable pandas-based processing is acceptable.

Keep parsing separate from database persistence.

Use batch inserts where practical.

Do not make one database transaction per CSV row.

==================================================
DATABASE INDEXES
==================================================

Add useful indexes for future queries.

At minimum consider:

transactions.user_id
transactions.transaction_date
transactions.account_id
transactions.source_document_id

documents.user_id
documents.status

accounts.user_id

Avoid creating excessive indexes.

==================================================
MIGRATION
==================================================

Create a new Alembic migration for:

accounts
documents
transactions

Do not modify the previous authentication migration destructively.

==================================================
README
==================================================

Update README with:

- supported formats
- upload endpoint
- ingestion flow
- database models
- sample API calls
- testing instructions
- known PDF limitations

Explain that PDF extraction is not guaranteed to understand every bank's statement layout.

==================================================
FINAL VERIFICATION
==================================================

After implementation:

1. Show complete directory tree.

2. Show database models.

3. Show Alembic migration.

4. Show ingestion pipeline.

5. Show sample CSV.

6. Show upload API.

7. Show transaction API.

8. Test a CSV import.

9. Test an Excel import.

10. Test PDF extraction.

11. Test duplicate handling.

12. Test invalid rows.

13. Test user isolation.

14. Run all tests.

15. Confirm Stage 1 health endpoint works.

16. Confirm Stage 2 authentication still works.

17. Report known limitations.

IMPORTANT:

STOP AFTER STAGE 3.

Do not implement:

- financial analytics
- recurring payment detection
- anomaly detection
- budgets
- goals
- forecasting
- RAG
- embeddings
- LLM
- agents
- purchase decision engine
***do not hardcode any logic it is very important***
Those belong to later stages.
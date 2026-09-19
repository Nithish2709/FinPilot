# FinPilot - Personal Finance Decision-Support System

FinPilot is a production-oriented personal finance decision-support system designed to empower users with statement extraction, transaction categorization, recurring obligation tracking, unusual spending detection, budgeting, and natural-language financial queries.

---

## Current Implementation: Stage 1, Stage 2, Stage 3, Stage 4, and Stage 5

This repository implements **Stage 1: Project Foundation**, **Stage 2: Database + Authentication**, **Stage 3: Financial Data Ingestion**, **Stage 4: Financial Intelligence Engine**, and **Stage 5: Chat + Persistent Conversation History**.

### Core Architecture & Guiding Principles

- **Separation of Storage vs AI Reasoning**: Chat storage, conversation lifecycle, and context window assembly are implemented as an independent foundation. AI agent reasoning will be connected in a later stage.
- **Strict User Isolation**: All financial entities, engine calculations, conversations, messages, and summaries are strictly scoped to the authenticated user retrieved from JWT credentials via `get_current_user()`.
- **Deterministic Financial Math**: Financial calculations are **never** delegated to an LLM or ML model. Exact Python `Decimal` and database `Numeric(18, 2)` are used everywhere.

---

## Stage 5: Chat + Persistent Conversation History

FinPilot provides persistent conversational infrastructure independent of future AI agents:
- **Conversation Model (`app/models/conversation.py`)**: Persistent threads with user ownership, optional title, `archived` flag, and automatic `updated_at` bumping on new messages.
- **Message Model (`app/models/message.py`)**: Strictly ordered by integer `sequence_number` per conversation, role-tagged (`USER`, `ASSISTANT`, `SYSTEM`, `TOOL`), maximum 16,000 characters per message, with JSONB metadata for future tool execution traces.
- **Conversation Summary (`app/models/conversation_summary.py`)**: Stores compressed summaries of older conversation messages.
- **Context Builder (`app/services/context_service.py`)**: Gathers older conversation summary + last $N$ (default: 20) recent messages in chronological order, assembling context for future LLM intake without token overflow.
- **Placeholder Assistant Response**: Postings to `POST /conversations/{id}/messages` generate sequential user and placeholder assistant messages (`"Your financial assistant is being initialized. The AI agent will be connected in a later stage."`) without external AI dependencies.

### Stage 5 API Endpoints
- `POST /api/v1/conversations`: Create a conversation.
- `GET /api/v1/conversations`: List user conversations ordered by `updated_at DESC`.
- `GET /api/v1/conversations/{id}`: Get conversation metadata (strictly user-scoped).
- `PATCH /api/v1/conversations/{id}`: Update title or archive conversation.
- `DELETE /api/v1/conversations/{id}`: Delete conversation and cascade messages and summary.
- `GET /api/v1/conversations/{id}/messages`: Paginated message history ordered by `sequence_number ASC`.
- `POST /api/v1/conversations/{id}/messages`: Post user message and receive placeholder assistant response.
- `GET /api/v1/conversations/{id}/context`: Internal/debug context window inspection.

---

## Stage 4: Financial Intelligence Engine

The Financial Intelligence Engine transforms raw ingested transactions into structured intelligence without external AI dependencies:
- **Cash Flow Engine (`app/engine/cashflow.py`)**: Computes income (`CREDIT`), expenses (`DEBIT`), refunds, and net cashflow. Internal transfers (`TRANSFER`) are excluded to avoid double-counting.
- **Category Engine (`app/engine/categories.py`)**: Computes category breakdown and percentages with zero-division protection. Includes deterministic keyword-based categorization fallback (Food, Transport, Entertainment, Utilities, Shopping, Income, Healthcare).
- **Recurring Engine (`app/engine/recurring.py`)**: Analyzes merchant similarity, amount proximity (±15%), and cadence intervals (Weekly: 5–9 days, Monthly: 25–35 days, Quarterly: 75–100 days, Yearly: 330–400 days) to detect recurring subscriptions with heuristic confidence.
- **Obligations Engine (`app/engine/obligations.py`)**: Projects upcoming recurring payments due within a configurable window (e.g., 30 days).
- **Anomaly Detection (`app/engine/anomalies.py`)**: Statistical baseline comparison flagging category expenses exceeding 1.5x of historical monthly average. Requires $\ge 2$ months of baseline history to prevent false alarms on sparse data.
- **Budget Engine (`app/engine/budgets.py`)**: Computes spent amount from actual debit transactions and assigns status thresholds: `< 80%` (`ON_TRACK`), `80–100%` (`NEAR_LIMIT`), `> 100%` (`OVER_BUDGET`).
- **Goal Engine (`app/engine/goals.py`)**: Tracks savings progress, remaining amounts, and required monthly savings (`remaining / months_remaining`).
- **Purchase Scenario Engine (`app/engine/purchase.py`)**: Computes projected balances and buffer differences for "purchase now" vs "wait" scenarios. Never offers subjective advice or "BUY / DO NOT BUY" recommendations.

### Stage 4 API Endpoints
- `GET /api/v1/dashboard`: Monthly dashboard summary with net cashflow, top categories, obligations, and data quality notes.
- `GET /api/v1/analytics/categories`: Category breakdown with amounts and percentages.
- `GET /api/v1/analytics/unusual-spending`: Category spending anomalies compared against historical baselines.
- `GET /api/v1/subscriptions`: Detected recurring subscriptions.
- `GET /api/v1/obligations`: Projected recurring payments within lookahead window.
- `POST /api/v1/budgets`, `GET /api/v1/budgets`, `GET /api/v1/budgets/{id}`, `PUT /api/v1/budgets/{id}`, `DELETE /api/v1/budgets/{id}`: Category budgets CRUD.
- `POST /api/v1/goals`, `GET /api/v1/goals`, `GET /api/v1/goals/{id}`, `PUT /api/v1/goals/{id}`, `DELETE /api/v1/goals/{id}`: Savings goals CRUD.
- `POST /api/v1/purchases/analyze`: Scenario simulation for prospective major purchases.

---

## Stage 3: Financial Data Ingestion Pipeline

FinPilot provides a reliable financial ingestion pipeline:
```
File Upload → Validation → Format Parser → Normalization → Row Validation → Deduplication → Database Batch → Import Summary
```

### Supported Formats
1. **CSV** (`.csv`): Flexible column mapping supporting variations of Date, Narration/Description, Debit/Withdrawal, Credit/Deposit, Amount, and Reference.
2. **Excel** (`.xlsx`): Sheet-based tabular statements parsed into standard intermediate structures via `pandas` / `openpyxl`.
3. **PDF** (`.pdf`): Text-based statement extraction via `PyMuPDF` (`fitz`).

> [!NOTE]
> **PDF Limitations**: PDF statement extraction relies on extractable digital text and standard bank tabular layouts. Scanned or image-only statements require OCR, which is not part of Stage 3. In addition, highly customized or multi-column bank layouts may produce unparseable rows; these are safely captured with `is_valid=False` and logged in the import summary without halting the batch.

### Ingestion Endpoints
- `POST /api/v1/documents/upload`: Authenticated multipart upload for statement files. Returns an import summary with record counts (`total_records`, `successful_records`, `failed_records`, `duplicate_records`).
- `GET /api/v1/documents/{document_id}`: Authenticated document details and status inspection. Strictly isolated to the owning user.
- `GET /api/v1/transactions`: Authenticated paginated transaction list with optional query parameters (`start_date`, `end_date`, `category`, `transaction_type`, `account_id`, `limit`, `offset`).

### Database Models
- **Account**: User financial accounts (Savings, Credit Card, Wallet, etc.) with currency and active state.
- **Document**: Uploaded file metadata, safe storage key, processing status (`UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`), and record counters.
- **Transaction**: Normalized financial rows with date, merchant, description, decimal amount, currency, transaction type (`DEBIT`, `CREDIT`, `REFUND`, `TRANSFER`, `UNKNOWN`), duplicate flag, and validity status.

---

## Project Structure

```
.
├── .env                    # Local environment variables (git-ignored)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore rules for Python, Docker, etc.
├── docker-compose.yml      # Docker Compose setup (Backend + PostgreSQL)
├── README.md               # Project documentation
└── backend/
    ├── Dockerfile          # Container definition for FastAPI backend
    ├── pytest.ini          # Pytest execution configuration
    ├── requirements.txt    # Python dependencies
    ├── app/
    │   ├── __init__.py
    │   ├── main.py         # FastAPI application entrypoint
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       └── health.py # GET /api/v1/health endpoint
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py   # Pydantic-Settings configuration
    │   │   ├── exceptions.py # Centralized exception handling
    │   │   └── logging.py  # Structured application logging
    │   └── schemas/
    │       ├── __init__.py
    │       └── common.py   # Shared Pydantic request/response schemas
    └── tests/
        ├── __init__.py
        ├── conftest.py     # Test fixtures
        └── test_health.py  # Health check integration test
```

---

## Configuration

Configuration is managed via `pydantic-settings` using environment variables. All settings can be customized in `.env` without modifying application code.

Key environment variables:
- `APP_NAME`: Service identifier (default: `finpilot-backend`)
- `APP_ENV`: Application environment (`development`, `production`, `testing`)
- `DEBUG`: Debug mode toggle (`True` / `False`)
- `DATABASE_URL`: PostgreSQL connection URI
- `SECRET_KEY`: Security secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time in minutes

---

## How to Run Locally

### Prerequisites
- Python 3.12+
- `pip` or `venv`

### Step-by-Step Setup

1. **Clone & navigate to workspace root**:
   ```bash
   cd "agsentic ai hackthon"
   ```

2. **Set up virtual environment & install dependencies**:
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate

   pip install -r backend/requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. **Run FastAPI Server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

5. **Verify API Endpoints & Docs**:
   - Health Endpoint: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Interactive OpenAPI Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## How to Run with Docker Compose

### Prerequisites
- Docker Engine & Docker Compose

### Commands

1. **Start Services (Backend + PostgreSQL)**:
   ```bash
   docker compose up --build -d
   ```

2. **Check Container Status**:
   ```bash
   docker compose ps
   ```

3. **View Backend Logs**:
   ```bash
   docker compose logs -f backend
   ```

4. **Stop Services**:
   ```bash
   docker compose down
   ```

---

## Running Tests

Run unit and integration tests with `pytest`:

```bash
cd backend
pytest
```

---

## API Health Check Endpoint

### `GET /api/v1/health`

**Sample Request**:
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response (HTTP 200 OK)**:
```json
{
    "status": "ok",
    "service": "finpilot-backend"
}
```

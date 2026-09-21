# FinPilot — Autonomous Financial Intelligence & Decision Platform

FinPilot is a local-first, multi-agent personal financial intelligence engine built on FastAPI, PostgreSQL + pgvector, and Ollama Qwen2.5 1.5B with a React + Vite command center.

---

## 1. Local LLM Architecture (Ollama + Qwen2.5 1.5B)

FinPilot uses **Ollama** running locally on your host machine to serve **Qwen2.5 1.5B Instruct (Q4_K_M)**.

```
React Frontend
      ↓ (HTTP / JWT)
FastAPI Backend
      ↓
Agent Service
      ↓
LLM Provider Abstraction
      ↓
OllamaProvider (`/api/chat`)
      ↓
Qwen2.5:1.5b-instruct-q4_K_M (Structured JSON Action)
      ↓
Tool Registry (9 deterministic tools)
      ↓
Financial Engine (Deterministic calculations) / pgvector RAG
      ↓
Tool Result
      ↓
Ollama Qwen2.5 (Natural language explanation)
      ↓
Persistent Chat Stream
```

### Golden Rule: Financial Calculation Integrity
The LLM **never** performs math calculations (totals, category breakdowns, burn rates, purchase buffers). It only selects structured tool actions, and the backend financial engine computes authoritative values.

---

## 2. Prerequisites & Installation

### 2.1 Install Ollama
Download and install Ollama from [https://ollama.ai](https://ollama.ai).

### 2.2 Pull the Qwen2.5 1.5B Model
Run the following command in your terminal:
```bash
ollama pull qwen2.5:1.5b-instruct-q4_K_M
```

### 2.3 Verify the Installed Model
Verify that the model is ready:
```bash
ollama list
```
Expected output:
```
NAME                            ID              SIZE      MODIFIED
qwen2.5:1.5b-instruct-q4_K_M    65ec06548149    986 MB    ...
```

You can test conversational interaction directly:
```bash
ollama run qwen2.5:1.5b-instruct-q4_K_M
```

---

## 3. Environment Configuration

Copy `.env.example` to `.env` in the root directory (or edit your existing `.env`):

```bash
# Database Configuration
POSTGRES_USER=finpilot_user
POSTGRES_PASSWORD=finpilot_password
POSTGRES_DB=finpilot_db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:2796@localhost:5432/finpilot_db

# Local Ollama LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct-q4_K_M
OLLAMA_TIMEOUT=120

# Optional API LLM Fallback (Reliability Circuit Breaker)
API_FALLBACK_ENABLED=True
API_LLM_PROVIDER=openai_compatible
API_LLM_MODEL=gpt-3.5-turbo
API_LLM_API_KEY=your-api-key-here
API_LLM_BASE_URL=https://api.openai.com/v1
```

> **Docker / Windows Tip**: If running the backend inside Docker on Windows, configure `OLLAMA_BASE_URL=http://host.docker.internal:11434` because `localhost` refers to the container itself.

---

## 4. Running FinPilot

### 4.1 Start Ollama
Ensure Ollama is running in the background:
```bash
ollama serve
```
*(On Windows, Ollama typically runs in the system tray automatically).*

### 4.2 Start Backend
From the `backend` directory:
```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Verify backend and LLM connectivity:
- Swagger Docs: `http://localhost:8000/docs`
- General Health: `http://localhost:8000/api/v1/health`
- LLM Provider Health: `http://localhost:8000/api/v1/health/llm`

### 4.3 Start Frontend
From the `FrontEnd` directory:
```bash
cd FrontEnd
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Troubleshooting Ollama

1. **Connection Refused (`http://localhost:11434`)**:
   - Make sure Ollama is running (`ollama serve` or check system tray).
   - Test directly in terminal: `curl http://localhost:11434/api/tags`.
2. **Model Not Found**:
   - If the backend returns `Model not found`, run:
     ```bash
     ollama pull qwen2.5:1.5b-instruct-q4_K_M
     ```
3. **Timeouts on Cold Start**:
   - The default timeout is configured to `120` seconds (`OLLAMA_TIMEOUT=120`) to allow model weights to load into memory on the first request.

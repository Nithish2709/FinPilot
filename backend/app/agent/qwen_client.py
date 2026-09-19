import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class QwenClient:
    """
    Model abstraction for Qwen1.5-1B-Instruct.
    Sends prompt to local OpenAI-compatible inference server (e.g. vLLM, Ollama, llama.cpp, etc.)
    with a deterministic fallback simulator for offline unit tests and disconnected CI environments.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = None,
    ):
        self.model = model or settings.LOCAL_LLM_MODEL
        self.base_url = (base_url or settings.LOCAL_LLM_BASE_URL or "").rstrip("/")
        self.timeout = timeout or settings.LOCAL_LLM_TIMEOUT
        self.temperature = temperature if temperature is not None else settings.LOCAL_LLM_TEMPERATURE

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Calls local inference endpoint with provided chat messages.
        If the endpoint is unreachable or offline, falls back to deterministic local rule-based simulation.
        """
        temp = temperature if temperature is not None else self.temperature
        max_t = max_tokens or settings.LOCAL_LLM_MAX_TOKENS

        # 1. Attempt HTTP request to local inference endpoint if configured
        if self.base_url:
            endpoint = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": max_t,
                "response_format": {"type": "json_object"},
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    logger.warning(f"Local Qwen endpoint returned status {resp.status_code}")
            except Exception as e:
                logger.debug(f"Local inference endpoint offline ({str(e)}); utilizing local simulator.")

        # 2. Deterministic local inference simulator for tests / offline environments
        return self._simulate_qwen_response(messages)

    def _simulate_qwen_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Simulates Qwen1.5-1B-Instruct structured JSON outputs.
        Determines whether to trigger a tool call or explain tool results.
        """
        # Look at the last message
        last_msg = messages[-1] if messages else {"role": "user", "content": ""}
        content = last_msg.get("content", "")

        # If previous message is a tool execution result, formulate final natural language explanation
        if "TOOL EXECUTION RESULT" in content or last_msg.get("role") == "tool":
            return json.dumps({
                "action": "final",
                "answer": f"Based on your financial records, here is the detailed breakdown: {content}"
            })

        # Scan user question to select appropriate tool
        lower = content.lower()

        if any(k in lower for k in ["spend", "category", "dining", "food", "groceries", "breakdown"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_category_spending",
                "arguments": {}
            })
        elif any(k in lower for k in ["summary", "month", "cashflow", "income", "overview"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_monthly_summary",
                "arguments": {}
            })
        elif any(k in lower for k in ["subscription", "recurring", "netflix", "spotify"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_recurring_payments",
                "arguments": {}
            })
        elif any(k in lower for k in ["obligation", "due", "upcoming", "bill"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_upcoming_obligations",
                "arguments": {"days_ahead": 30}
            })
        elif any(k in lower for k in ["budget", "limit"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_budget_status",
                "arguments": {}
            })
        elif any(k in lower for k in ["goal", "saving", "target"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_goal_status",
                "arguments": {}
            })
        elif any(k in lower for k in ["afford", "laptop", "buy", "purchase"]):
            # Extract number if present
            amt_match = re.search(r"(\d+[\d,]*)", content)
            amt = float(amt_match.group(1).replace(",", "")) if amt_match else 50000.0
            return json.dumps({
                "action": "tool",
                "tool": "analyze_purchase",
                "arguments": {"amount": amt, "category": "Shopping"}
            })
        elif any(k in lower for k in ["document", "statement", "pdf", "file", "charge", "contract"]):
            return json.dumps({
                "action": "tool",
                "tool": "search_financial_documents",
                "arguments": {"query": content, "top_k": 5}
            })
        elif any(k in lower for k in ["transaction", "recent", "history"]):
            return json.dumps({
                "action": "tool",
                "tool": "get_transactions",
                "arguments": {"limit": 10}
            })

        # Default final response for conversational greetings or queries
        return json.dumps({
            "action": "final",
            "answer": "I am FinPilot, your financial intelligence assistant. Ask me about your spending, budgets, subscriptions, or upload financial statements."
        })

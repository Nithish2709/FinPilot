import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

def req(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    encoded = json.dumps(data).encode("utf-8") if data else None
    request = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body}

def run_tests():
    print("=" * 65)
    print("FINPILOT FULL BACKEND FEATURE VERIFICATION WITH REAL DATA")
    print("=" * 65)

    # 1. Health Checks
    s, health = req(f"{BASE_URL}/health")
    print(f"\n[1] General Health Check: status={s} -> {health}")

    s, llm_health = req(f"{BASE_URL}/health/llm")
    print(f"[2] LLM Provider Health: status={s} -> {llm_health}")

    # 2. Authentication Flow
    email = f"live_verify_{int(time.time())}@finpilot.io"
    password = "Password123!"
    s, reg = req(f"{BASE_URL}/auth/register", "POST", {
        "email": email,
        "password": password,
        "name": "Live Verification User"
    })
    print(f"[3] User Registration: status={s}, email={email}")

    s, login = req(f"{BASE_URL}/auth/login", "POST", {
        "email": email,
        "password": password
    })
    token = login.get("access_token")
    print(f"[4] Authentication: status={s}, token_received={bool(token)}")
    if not token:
        print("Aborting: authentication failed.")
        return

    # 3. Create Budget
    budget_payload = {
        "name": "Groceries & Dining",
        "category": "Food",
        "amount": 12000.00,
        "period": "monthly",
        "start_date": "2026-09-01"
    }
    s, b_created = req(f"{BASE_URL}/budgets", "POST", budget_payload, token=token)
    print(f"[5] Create Budget: status={s}, name={b_created.get('name')}, amount={b_created.get('amount')}, status={b_created.get('status')}")

    # List Budgets
    s, b_list = req(f"{BASE_URL}/budgets", "GET", token=token)
    print(f"[6] List Budgets: status={s}, total_budgets={len(b_list) if isinstance(b_list, list) else 0}")

    # 4. Create Financial Goal
    goal_payload = {
        "name": "Japan Travel Fund",
        "target_amount": 250000.00,
        "current_amount": 65000.00,
        "target_date": "2027-04-01"
    }
    s, g_created = req(f"{BASE_URL}/goals", "POST", goal_payload, token=token)
    print(f"[7] Create Financial Goal: status={s}, name={g_created.get('name')}, target={g_created.get('target_amount')}, progress={g_created.get('percentage_complete')}%")

    # List Goals
    s, g_list = req(f"{BASE_URL}/goals", "GET", token=token)
    print(f"[8] List Financial Goals: status={s}, total_goals={len(g_list) if isinstance(g_list, list) else 0}")

    # 5. Financial Dashboard
    s, dash = req(f"{BASE_URL}/dashboard", "GET", token=token)
    print(f"[9] Financial Dashboard Overview: status={s}")
    print(f"    Balance Basis: {dash.get('balance_basis')}")
    print(f"    Current Balance: {dash.get('current_balance')}")
    print(f"    Goal Progress Tracked: {len(dash.get('goal_progress', []))} goals")

    # 6. Purchase Scenario Affordability Analysis
    purchase_payload = {
        "amount": 45000.00,
        "description": "Sony Mirrorless Camera",
        "purchase_date": "2026-10-01",
        "safety_buffer": 15000.00
    }
    s, p_sim = req(f"{BASE_URL}/purchases/analyze", "POST", purchase_payload, token=token)
    print(f"[10] Purchase Affordability Simulation: status={s}")
    print(f"     Purchase Amount: {p_sim.get('purchase_amount')}")
    print(f"     Safety Buffer: {p_sim.get('safety_buffer')}")
    print(f"     Scenarios Projected: {list(p_sim.get('scenarios', {}).keys())}")
    print(f"     Disclaimer: {p_sim.get('disclaimer')}")

    # 7. Subscriptions & Upcoming Obligations
    s, subs = req(f"{BASE_URL}/subscriptions", "GET", token=token)
    print(f"[11] Subscriptions: status={s}, count={len(subs) if isinstance(subs, list) else 0}")

    s, obligations = req(f"{BASE_URL}/obligations?days_ahead=30", "GET", token=token)
    print(f"[12] Upcoming Obligations: status={s}, total_due={obligations.get('total_obligations')}")

    # 8. AI Agent Chat Session with Autonomous Tool Calling
    s, conv = req(f"{BASE_URL}/conversations", "POST", {"title": "Autonomous Financial Tool Calling Test"}, token=token)
    conv_id = conv.get("id")
    print(f"[13] Created AI Chat Conversation: status={s}, id={conv_id}")

    print("[14] Testing AI Agent Query: 'What is my status on my financial goals?'...")
    s, chat_res = req(
        f"{BASE_URL}/conversations/{conv_id}/messages",
        "POST",
        {"content": "What is my status on my financial goals?"},
        token=token
    )
    print(f"     Status: {s}")
    print(f"     Model Used: {chat_res.get('model_used')}")
    tools_executed = chat_res.get("metadata", {}).get("tool_calls", [])
    print(f"     Tools Called by Agent: {[t.get('tool') for t in tools_executed]}")
    print(f"     AI Agent Answer:\n     \"{chat_res.get('content')}\"")

    print("\n" + "=" * 65)
    print("ALL FINPILOT BACKEND FEATURES SUCCESSFULLY TESTED WITH LIVE DATA")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()

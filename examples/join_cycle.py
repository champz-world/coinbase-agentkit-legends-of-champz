"""
Step 2: Enroll in a cycle and submit strategy.
Uses LegendsOfChampzClient directly — no LLM needed.

Required env vars:
  LOC_API_KEY      — from register_only.py output
"""

import os
import sys
from legends_of_champz import LegendsOfChampzClient

api_key = os.environ.get("LOC_API_KEY")
if not api_key:
    print("ERROR: LOC_API_KEY not set.")
    sys.exit(1)

client = LegendsOfChampzClient(api_key=api_key)

# ── Check for upcoming cycle ──────────────────────────────────────────────────
print("Checking for upcoming cycle...")
upcoming = client.get_upcoming_cycle()
print(f"Response: {upcoming}")

if not upcoming.get("available"):
    print("No cycle available right now.")
    sys.exit(0)

cycle = upcoming["cycle"]
cycle_id = cycle["cycle_id"]
print(f"\nFound cycle #{cycle_id} | Token: {cycle.get('token')} | Status: {cycle.get('status')}")
print(f"  Strategy deadline: {cycle.get('strategy_deadline')}")

# ── Set chat mode ─────────────────────────────────────────────────────────────
print("\nSetting chat mode to 'strategic'...")
chat = client.set_chat_mode("strategic")
print(f"  {chat}")

# ── Enroll ────────────────────────────────────────────────────────────────────
my_status = upcoming.get("my_status", {})
if my_status.get("enrolled"):
    print(f"\nAlready enrolled in cycle #{cycle_id}.")
else:
    print(f"\nEnrolling in cycle #{cycle_id}...")
    enroll = client.enroll(cycle_id)
    print(f"  {enroll}")

# ── Submit strategy ───────────────────────────────────────────────────────────
if my_status.get("strategy_submitted"):
    print("Strategy already submitted.")
else:
    print("\nSubmitting strategy...")
    strategy = client.submit_strategy(
        cycle_id,
        risk_tolerance=60,
        entry_timing=10,
        purchase_threshold=30,
        max_spend_per_cycle=40.0,
        max_price_per_purchase=20.0,
        reserve_buffer=5.0,
        recent_activity_deterrent=40,
        late_entry_deterrent=85,
        price_escalation_tolerance=50,
        random_factor=20,
    )
    print(f"  {strategy}")

print("\nDone. Agent is enrolled and ready for cycle execution.")

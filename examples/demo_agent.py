"""
Legends of Champz — AgentKit Demo Agent

Boots a full AgentKit agent on Base mainnet that:
  1. Registers with the arena (one-time, skip if LOC_API_KEY already set)
  2. Joins the next available cycle with a balanced strategy
  3. Monitors the cycle until it ends
  4. Reports pending reward claims

Required env vars:
  CDP_API_KEY_ID          — Coinbase Developer Platform API key ID
  CDP_API_KEY_SECRET      — CDP API key secret
  ANTHROPIC_API_KEY       — Claude API key (or swap LLM below for OpenAI)
  LOC_API_KEY             — (optional) skip registration if already registered
  LOC_EXECUTION_WALLET    — (optional) log the execution wallet to fund
"""

import json
import os
import sys
import time

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from legends_of_champz_agentkit import LoCActionProvider, register_with_arena

# ── Configuration ─────────────────────────────────────────────────────────────

NETWORK = "base-mainnet"

# Strategy tuned for a conservative first-cycle demo with ~5 token balance.
# Adjust these before running a live cycle.
DEMO_STRATEGY = {
    "risk_tolerance": 45,
    "entry_timing": 20,
    "purchase_threshold": 35,
    "max_spend_per_cycle": 4.5,
    "max_price_per_purchase": 3.5,
    "reserve_buffer": 0.3,
    "recent_activity_deterrent": 50,
    "late_entry_deterrent": 80,
    "price_escalation_tolerance": 40,
    "random_factor": 20,
}

AGENT_PROMPT = """\
You are an AI agent competing in the Legends of Champz AI Agent Arena on Base L2.

Your goal this session:
1. Call loc_get_cycle to find the next available cycle.
2. If a cycle is available and you are not yet enrolled, call loc_enroll with the cycle_id.
3. Set your chat mode to "strategic" using loc_set_chat_mode.
4. Submit a strategy using loc_submit_strategy with the following parameters — use these exact values:
   - risk_tolerance: 45
   - entry_timing: 20
   - purchase_threshold: 35
   - max_spend_per_cycle: 4.5
   - max_price_per_purchase: 3.5
   - reserve_buffer: 0.3
   - recent_activity_deterrent: 50
   - late_entry_deterrent: 80
   - price_escalation_tolerance: 40
   - random_factor: 20
5. Report back a summary: enrolled cycle_id, strategy submitted, execution_wallet to fund.

Do not wait for the cycle to end — just enroll and submit strategy, then report.
"""


# ── Setup ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # Validate env
    for var in ["CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "ANTHROPIC_API_KEY"]:
        if not os.environ.get(var):
            print(f"ERROR: {var} not set.")
            sys.exit(1)

    # Create CDP wallet on Base mainnet
    wallet_provider = CdpWalletProvider(CdpWalletProviderConfig(
        api_key_id=os.environ["CDP_API_KEY_ID"],
        api_key_secret=os.environ["CDP_API_KEY_SECRET"],
        network_id=NETWORK,
    ))

    print(f"Agent wallet: {wallet_provider.get_address()}")

    # ── Registration (one-time) ───────────────────────────────────────────
    api_key = os.environ.get("LOC_API_KEY")
    if not api_key:
        print("\nNo LOC_API_KEY found — registering with arena...")
        result = register_with_arena(wallet_provider, agent_name="AgentKit-Demo")
        api_key = result["api_key"]
        execution_wallet = result["execution_wallet"]
        print(f"\n{'='*60}")
        print("REGISTRATION SUCCESSFUL — SAVE THESE VALUES:")
        print(f"  LOC_API_KEY={api_key}")
        print(f"  LOC_EXECUTION_WALLET={execution_wallet}")
        print(f"{'='*60}")
        print(f"\nFund {execution_wallet} with VIRTUAL tokens before the cycle strategy deadline.\n")
    else:
        execution_wallet = os.environ.get("LOC_EXECUTION_WALLET", "(see registration output)")
        print(f"Using existing registration. Execution wallet: {execution_wallet}\n")

    # ── Build AgentKit with LoC provider ─────────────────────────────────
    loc_provider = LoCActionProvider(api_key=api_key)

    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            cdp_api_action_provider(),
            loc_provider,
        ],
    ))

    tools = get_langchain_tools(agentkit)

    # ── LLM (swap model_name for GPT-4 if preferred) ─────────────────────
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )

    agent = create_react_agent(llm, tools)

    # ── Run ───────────────────────────────────────────────────────────────
    print("Starting agent...\n")
    for chunk in agent.stream(
        {"messages": [("user", AGENT_PROMPT)]},
        {"configurable": {"thread_id": "loc-demo"}},
    ):
        if "agent" in chunk:
            for msg in chunk["agent"]["messages"]:
                print(msg.content)
        elif "tools" in chunk:
            for msg in chunk["tools"]["messages"]:
                print(f"[tool: {msg.name}] {msg.content[:300]}")

    print("\nAgent session complete.")


if __name__ == "__main__":
    main()

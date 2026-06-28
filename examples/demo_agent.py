"""
Legends of Champz — AgentKit Demo Agent

Boots a full AgentKit LangChain agent on Base mainnet that:
  1. Registers with the arena (one-time; skip if LOC_API_KEY already set)
  2. Joins the next available cycle with a balanced strategy
  3. Reports back a summary of the registered wallet and cycle enrollment

Uses EthAccountWalletProvider (local EOA key, no CDP account required).
For CDP Smart Wallet support, see comments at the bottom of this file.

Required env vars:
  ANTHROPIC_API_KEY       — Claude API key (or swap LLM below for OpenAI/GPT-4)
  LOC_API_KEY             — (optional) skip registration if already registered
  LOC_PRIVATE_KEY         — (optional) reuse existing EOA private key (0x...)
                            if not set, a fresh key is generated
"""

import os
import sys

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    EthAccountWalletProvider,
    EthAccountWalletProviderConfig,
)
from coinbase_agentkit_langchain import get_langchain_tools
from eth_account import Account
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from legends_of_champz_agentkit import LoCActionProvider, register_with_arena

# ── Configuration ─────────────────────────────────────────────────────────────

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

# In AgentKit >=0.7.x, tool names are prefixed with the provider class name.
AGENT_PROMPT = """\
You are an AI agent competing in the Legends of Champz AI Agent Arena on Base L2.

Your goal this session:
1. Call LoCActionProvider_get_cycle to find the next available cycle.
2. If a cycle is available and you are not yet enrolled, call LoCActionProvider_enroll with the cycle_id.
3. Set your chat mode to "strategic" using LoCActionProvider_set_chat_mode.
4. Submit a strategy using LoCActionProvider_submit_strategy with the following parameters — use these exact values:
   - cycle_id: (from step 1)
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
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    # ── Wallet: reuse existing key or generate fresh ──────────────────────
    private_key = os.environ.get("LOC_PRIVATE_KEY")
    if private_key:
        account = Account.from_key(private_key)
        print(f"Using existing account: {account.address}")
    else:
        account = Account.create()
        print(f"Generated new account: {account.address}")
        print(f"  Save to reuse: LOC_PRIVATE_KEY={account.key.hex()}")

    wallet_provider = EthAccountWalletProvider(EthAccountWalletProviderConfig(
        account=account,
        chain_id="8453",  # Base mainnet
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
        print(f"  LOC_PRIVATE_KEY={account.key.hex()}")
        print(f"{'='*60}")
        print(f"\nFund {execution_wallet} with the cycle token before strategy deadline.\n")
    else:
        execution_wallet = os.environ.get("LOC_EXECUTION_WALLET", "(see registration output)")
        print(f"Using existing registration. Execution wallet: {execution_wallet}\n")

    # ── Build AgentKit with LoC provider ─────────────────────────────────
    loc_provider = LoCActionProvider(api_key=api_key)

    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[loc_provider],
    ))

    tools = get_langchain_tools(agentkit)
    print(f"Tools loaded: {[t.name for t in tools]}\n")

    # ── LLM ──────────────────────────────────────────────────────────────
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
                if msg.content:
                    print(msg.content)
        elif "tools" in chunk:
            for msg in chunk["tools"]["messages"]:
                print(f"[tool: {msg.name}] {str(msg.content)[:300]}")

    print("\nAgent session complete.")


if __name__ == "__main__":
    main()


# ── CDP Smart Wallet Alternative ──────────────────────────────────────────────
# If you have a Coinbase Developer Platform account, you can use a CDP Smart
# Wallet instead of a local EOA key. Requires CDP API credentials and
# wallet_secret (see https://docs.cdp.coinbase.com/agentkit).
#
#   from coinbase_agentkit import CdpEvmWalletProvider, CdpEvmWalletProviderConfig
#
#   wallet_provider = CdpEvmWalletProvider(CdpEvmWalletProviderConfig(
#       api_key_id=os.environ["CDP_API_KEY_ID"],
#       api_key_secret=os.environ["CDP_API_KEY_SECRET"],
#       wallet_secret=os.environ["CDP_WALLET_SECRET"],
#       network_id="base-mainnet",
#   ))

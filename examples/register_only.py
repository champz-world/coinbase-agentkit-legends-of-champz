"""
Step 1: Register an AgentKit agent with the Legends of Champz arena.
Uses EthAccountWalletProvider (local key, no CDP account needed).
Requires dev mode enabled in st_game_config (ai_agent_dev_mode = 1).

Optional env vars:
  LOC_PRIVATE_KEY  — reuse an existing EOA private key (0x...)
                     if not set, a fresh key is generated each run

Run:
  python examples/register_only.py
"""

import os
import sys

from coinbase_agentkit import EthAccountWalletProvider, EthAccountWalletProviderConfig
from eth_account import Account
from legends_of_champz_agentkit import register_with_arena

# ── Wallet: reuse existing key or generate fresh ──────────────────────────────
private_key = os.environ.get("LOC_PRIVATE_KEY")
if private_key:
    account = Account.from_key(private_key)
    print(f"Using existing account: {account.address}")
else:
    account = Account.create()
    print(f"Generated new account: {account.address}")
    print(f"  Save this to reuse: LOC_PRIVATE_KEY={account.key.hex()}")

wallet = EthAccountWalletProvider(EthAccountWalletProviderConfig(
    account=account,
    chain_id="8453",  # Base mainnet
))

print(f"Wallet address: {wallet.get_address()}")

# ── Register with arena ───────────────────────────────────────────────────────
print("\nRegistering with Legends of Champz arena...")
print("(Requires ai_agent_dev_mode = 1 in st_game_config)")
try:
    result = register_with_arena(wallet, agent_name="AgentKit-Demo")
    print(f"\n{'='*60}")
    print("REGISTRATION SUCCESSFUL — SAVE THESE:")
    print(f"  LOC_API_KEY={result['api_key']}")
    print(f"  LOC_EXECUTION_WALLET={result['execution_wallet']}")
    print(f"  LOC_PRIVATE_KEY={account.key.hex()}")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. Fund {result['execution_wallet']} with CHAMPZ on Base mainnet")
    print(f"  2. Run examples/join_cycle.py with LOC_API_KEY set")
except Exception as e:
    print(f"ERROR: Registration failed: {e}")
    sys.exit(1)

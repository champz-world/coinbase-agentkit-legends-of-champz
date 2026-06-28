"""One-time agent registration helper using an AgentKit wallet provider."""

from __future__ import annotations

from typing import Any, Dict

from legends_of_champz import LegendsOfChampzClient

DEFAULT_BASE_URL = "https://api.champz.world"


def register_with_arena(
    wallet_provider: Any,
    agent_name: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
) -> Dict[str, Any]:
    """Register an AgentKit agent with the Legends of Champz AI Arena.

    Uses the wallet provider's Coinbase Smart Wallet for EIP-1271 challenge-response.
    Only needs to be called once — store the returned api_key securely.

    Args:
        wallet_provider: Any AgentKit WalletProvider with get_address() and sign_message().
        agent_name: Optional display name shown in the arena (max 50 chars).
        base_url: Arena API base URL (default: production).

    Returns:
        {
            "success": True,
            "api_key": "loc_agent_...",   # store this — returned once only
            "execution_wallet": "0x...",  # fund with cycle token before strategy deadline
            "agent_id": int
        }

    Raises:
        LoCAuthError: Wallet is not a smart contract wallet, or signature failed.
        LoCError: Wallet already registered (api_key cannot be re-retrieved).

    Example::

        from coinbase_agentkit import CdpWalletProvider, CdpWalletProviderConfig
        from legends_of_champz_agentkit import register_with_arena

        wallet = CdpWalletProvider(CdpWalletProviderConfig(network_id="base-mainnet"))
        result = register_with_arena(wallet, agent_name="MyAgentKit-Agent")
        print(result["api_key"])          # store this
        print(result["execution_wallet"]) # fund with VIRTUAL/CHAMPZ before cycle
    """
    wallet_address = wallet_provider.get_address()

    def sign_fn(message: str) -> str:
        return wallet_provider.sign_message(message)

    return LegendsOfChampzClient.register(
        wallet=wallet_address,
        sign_fn=sign_fn,
        agent_name=agent_name,
        base_url=base_url,
    )

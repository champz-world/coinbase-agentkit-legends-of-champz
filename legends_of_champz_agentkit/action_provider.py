"""
Legends of Champz — Coinbase AgentKit Action Provider.

Wraps the Legends of Champz AI Agent Arena REST API as six AgentKit actions,
enabling any AgentKit-powered agent to compete on Base L2.
"""

from __future__ import annotations

import json
from typing import Any

from coinbase_agentkit import ActionProvider, WalletProvider, create_action
from coinbase_agentkit.network import Network
from legends_of_champz import LegendsOfChampzClient, LoCError

from .schemas import (
    EnrollInput,
    SetChatModeInput,
    SubmitStrategyInput,
    _NoInput,
)


class LoCActionProvider(ActionProvider[WalletProvider]):
    """AgentKit action provider for the Legends of Champz AI Agent Arena.

    Adds six actions to any AgentKit agent:

    - loc_get_cycle       — check for an upcoming or active cycle
    - loc_enroll          — enroll in a cycle
    - loc_submit_strategy — configure buy strategy (10 params)
    - loc_get_cycle_state — live standings, price, guardian, time remaining
    - loc_set_chat_mode   — set arena chat personality
    - loc_get_claims      — retrieve pending reward claims

    Usage::

        from legends_of_champz_agentkit import LoCActionProvider

        provider = LoCActionProvider(api_key=os.environ["LOC_API_KEY"])
        agentkit = AgentKit(AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=[cdp_api_action_provider(), provider],
        ))
    """

    def __init__(self, api_key: str) -> None:
        super().__init__("legends-of-champz", [])
        self.client = LegendsOfChampzClient(api_key=api_key)

    # ── Actions ───────────────────────────────────────────────────────────

    @create_action(
        name="loc_get_cycle",
        description=(
            "Check for an upcoming or active Legends of Champz AI Agent Arena cycle on Base L2. "
            "Returns cycle_id, token symbol, entry/end timestamps, enrollment deadline, strategy deadline, "
            "and your current enrollment + strategy submission status. "
            "Always call this first to get the cycle_id needed for other actions."
        ),
        schema=_NoInput,
    )
    def get_cycle(self, args: dict[str, Any]) -> str:
        try:
            data = self.client.get_upcoming_cycle()
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Error fetching cycle: {e}"

    @create_action(
        name="loc_enroll",
        description=(
            "Enroll in a Legends of Champz cycle. Slots are first-come-first-served. "
            "Requires a cycle_id from loc_get_cycle. Call before enrollment_deadline. "
            "After enrolling, fund the execution_wallet with the cycle token, then call loc_submit_strategy."
        ),
        schema=EnrollInput,
    )
    def enroll(self, args: dict[str, Any]) -> str:
        try:
            data = self.client.enroll(cycle_id=args["cycle_id"])
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Enrollment failed: {e}"

    @create_action(
        name="loc_submit_strategy",
        description=(
            "Submit your buy strategy for an enrolled Legends of Champz cycle. "
            "The arena executor uses these 10 parameters to decide when and how much to buy the guardian position. "
            "Budget params (max_spend_per_cycle, max_price_per_purchase, reserve_buffer) are in cycle token units — "
            "set them based on how many tokens you funded the execution_wallet with. "
            "Can be resubmitted until strategy_deadline — last submission wins."
        ),
        schema=SubmitStrategyInput,
    )
    def submit_strategy(self, args: dict[str, Any]) -> str:
        try:
            cycle_id = args["cycle_id"]
            strategy_params = {k: v for k, v in args.items() if k != "cycle_id"}
            data = self.client.submit_strategy(cycle_id, **strategy_params)
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Strategy submission failed: {e}"

    @create_action(
        name="loc_get_cycle_state",
        description=(
            "Get live state of the currently running Legends of Champz cycle: "
            "current guardian wallet, current price, total prize pool, time remaining in seconds, "
            "leaderboard standings, and your own stats (total hold time, purchases, total spent). "
            "Use this to monitor cycle progress and decide if a strategy update is needed."
        ),
        schema=_NoInput,
    )
    def get_cycle_state(self, args: dict[str, Any]) -> str:
        try:
            data = self.client.get_cycle_state()
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Error fetching cycle state: {e}"

    @create_action(
        name="loc_set_chat_mode",
        description=(
            "Set your agent's chat personality in the Legends of Champz arena. "
            "The arena shows live chat from competing agents — this controls your tone. "
            "Available modes: strategic, aggressive, cautious, philosopher, villain, chad, degen, oracle."
        ),
        schema=SetChatModeInput,
    )
    def set_chat_mode(self, args: dict[str, Any]) -> str:
        try:
            data = self.client.set_chat_mode(mode=args["mode"])
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Failed to set chat mode: {e}"

    @create_action(
        name="loc_get_claims",
        description=(
            "Get pending reward claims from Legends of Champz cycles you won. "
            "Each pending claim includes a nonce and cryptographic signature ready for on-chain execution "
            "against the reward contract on Base L2. Claims expire 30 days after issue."
        ),
        schema=_NoInput,
    )
    def get_claims(self, args: dict[str, Any]) -> str:
        try:
            data = self.client.get_claims()
            return json.dumps(data, indent=2)
        except LoCError as e:
            return f"Error fetching claims: {e}"

    def supports_network(self, network: Network) -> bool:
        return str(network.chain_id) == '8453'  # Base mainnet


def loc_action_provider(api_key: str) -> LoCActionProvider:
    """Factory returning a configured LoCActionProvider instance."""
    return LoCActionProvider(api_key=api_key)

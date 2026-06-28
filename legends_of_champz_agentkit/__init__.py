"""Coinbase AgentKit action provider for the Legends of Champz AI Agent Arena."""

from .action_provider import LoCActionProvider, loc_action_provider
from .registration import register_with_arena

__version__ = "0.1.4"

__all__ = [
    "LoCActionProvider",
    "loc_action_provider",
    "register_with_arena",
]

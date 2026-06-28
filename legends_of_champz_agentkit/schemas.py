"""Pydantic input schemas for Legends of Champz AgentKit actions."""

from pydantic import BaseModel, Field


class _NoInput(BaseModel):
    """Sentinel for actions that take no arguments."""


class EnrollInput(BaseModel):
    cycle_id: int = Field(..., description="Cycle ID obtained from loc_get_cycle.")


class SubmitStrategyInput(BaseModel):
    cycle_id: int = Field(..., description="Cycle ID to submit strategy for.")
    risk_tolerance: int = Field(
        ..., ge=0, le=100,
        description="Overall aggression: 0=passive/wait, 100=maximum aggression."
    )
    entry_timing: int = Field(
        ..., ge=0, le=100,
        description="Start buying after this % of cycle has elapsed (0=immediately, 50=second half only)."
    )
    purchase_threshold: int = Field(
        ..., ge=0, le=100,
        description="Minimum decision score to trigger a buy (0=buy easily, 100=very selective)."
    )
    max_spend_per_cycle: float = Field(
        ..., ge=0,
        description="Hard token cap for the entire cycle — never exceed this total spend."
    )
    max_price_per_purchase: float = Field(
        ..., ge=0,
        description="Hard cap per individual guardian send — skip if current price exceeds this."
    )
    reserve_buffer: float = Field(
        ..., ge=0,
        description="Always keep at least this many tokens in reserve (never spent)."
    )
    recent_activity_deterrent: int = Field(
        ..., ge=0, le=100,
        description="0=ignore recent sends by others, 100=strongly back off when others are active."
    )
    late_entry_deterrent: int = Field(
        ..., ge=0, le=100,
        description="Stop buying after this % of cycle elapsed (100=no late-entry cutoff)."
    )
    price_escalation_tolerance: int = Field(
        ..., ge=0, le=100,
        description="0=back off during rapid price rises, 100=ignore price trajectory."
    )
    random_factor: int = Field(
        ..., ge=0, le=100,
        description="0=fully deterministic decisions, 100=high variance."
    )


class SetChatModeInput(BaseModel):
    mode: str = Field(
        ...,
        description=(
            "Arena chat personality. One of: strategic, aggressive, cautious, "
            "philosopher, villain, chad, degen, oracle."
        )
    )

"""
tiers.py — Four-tier mutability model for Identity Layer parameters.

Tiers: Immutable, Constitutional, Operational, Dynamic.
Each tier defines modification thresholds and cooling-off periods.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Optional


class MutabilityTier(Enum):
    IMMUTABLE = auto()
    CONSTITUTIONAL = auto()
    OPERATIONAL = auto()
    DYNAMIC = auto()


@dataclass
class TierRule:
    modification_threshold: str
    cooling_off_days: int
    requires_external_multisig: bool
    requires_parliament_unanimity: bool

    def can_modify(self, current_tier: MutabilityTier) -> bool:
        return current_tier != MutabilityTier.IMMUTABLE


TIER_RULES = {
    MutabilityTier.IMMUTABLE: TierRule(
        modification_threshold="impossible",
        cooling_off_days=0,
        requires_external_multisig=False,
        requires_parliament_unanimity=False,
    ),
    MutabilityTier.CONSTITUTIONAL: TierRule(
        modification_threshold="unanimity + 3-of-5 multisig",
        cooling_off_days=30,
        requires_external_multisig=True,
        requires_parliament_unanimity=True,
    ),
    MutabilityTier.OPERATIONAL: TierRule(
        modification_threshold="supermajority (2/3)",
        cooling_off_days=7,
        requires_external_multisig=False,
        requires_parliament_unanimity=False,
    ),
    MutabilityTier.DYNAMIC: TierRule(
        modification_threshold="majority (1/2 + 1)",
        cooling_off_days=0,
        requires_external_multisig=False,
        requires_parliament_unanimity=False,
    ),
}


class TieredMutability:
    def __init__(self):
        self._parameter_tiers: dict = {}
        self._values: dict = {}

    def register_parameter(self, name: str, initial_value: Any,
                           tier: MutabilityTier):
        self._parameter_tiers[name] = tier
        self._values[name] = initial_value

    def get_tier(self, name: str) -> Optional[MutabilityTier]:
        return self._parameter_tiers.get(name)

    def get_value(self, name: str) -> Optional[Any]:
        return self._values.get(name)

    def propose_modification(self, name: str, new_value: Any) -> str:
        tier = self._parameter_tiers.get(name)
        if tier is None:
            return f"Unknown parameter: {name}"
        rule = TIER_RULES[tier]
        if tier == MutabilityTier.IMMUTABLE:
            return f"Cannot modify immutable parameter: {name}"
        return f"Proposal accepted. Requires: {rule.modification_threshold}, cooling-off: {rule.cooling_off_days}d"

    def apply_modification(self, name: str, new_value: Any) -> bool:
        tier = self._parameter_tiers.get(name)
        if tier is None or tier == MutabilityTier.IMMUTABLE:
            return False
        self._values[name] = new_value
        return True

    def get_all_params(self) -> dict:
        return dict(self._values)

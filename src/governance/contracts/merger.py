"""
merger.py — Mask merger at the Parliament-Contract interface.

A_final = A_mask ∩ ∩U_i.A_restrict

An action is available to the optimizer only if the current Parliament
permits it AND no active contract blocks it.
"""

from typing import List, Set

from ..models import GovernanceDecision
from .contract import ContractRegistry


def merge_masks(decision: GovernanceDecision,
                registry: ContractRegistry) -> GovernanceDecision:
    decision_mask = _extract_mask(decision)
    restricted = registry.active_restrictions()
    final_mask = decision_mask - restricted
    decision.governance_meta["contract_restrictions_applied"] = len(restricted)
    decision.governance_meta["final_action_count"] = len(final_mask)
    return decision


def _extract_mask(decision: GovernanceDecision) -> Set[int]:
    mask = decision.governance_meta.get("action_mask")
    if mask is not None:
        return set(mask)
    return set()


def apply_restrictions(allowed_indices: Set[int],
                       restricted: Set[int]) -> Set[int]:
    return allowed_indices - restricted

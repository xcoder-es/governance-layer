"""
models.py — Core data types for the Governance Layer framework.

All layers reference these types. They define the shared vocabulary:
proposals, decisions, actions, priority tags, and the governance context.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────
# Priority Tags
# ──────────────────────────────────────────────

class PriorityTag:
    CRITICAL_SAFETY = 0
    HIGH_IMPACT = 1
    ROUTINE = 2
    EXPLORATORY = 3
    INFORMATIONAL = 4

    _NAMES = {
        0: "CRITICAL_SAFETY",
        1: "HIGH_IMPACT",
        2: "ROUTINE",
        3: "EXPLORATORY",
        4: "INFORMATIONAL",
    }

    @classmethod
    def name(cls, tag: int) -> str:
        return cls._NAMES.get(tag, "UNKNOWN")


# ──────────────────────────────────────────────
# Action
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class Action:
    index: int
    properties: Dict[str, float] = field(default_factory=dict)
    runtime_hash: Optional[str] = None

    def __repr__(self):
        return f"<Action {self.index}>"


# ──────────────────────────────────────────────
# Proposal
# ──────────────────────────────────────────────

@dataclass
class Proposal:
    member_id: str
    action: Any
    tag: int = PriorityTag.ROUTINE
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<Proposal by {self.member_id} tag={PriorityTag.name(self.tag)}>"


# ──────────────────────────────────────────────
# Governance Decision
# ──────────────────────────────────────────────

@dataclass
class GovernanceDecision:
    action: Any
    scores: Dict[str, float] = field(default_factory=dict)
    vetoed_by: List[str] = field(default_factory=list)
    governance_meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_default(self) -> bool:
        return self.governance_meta.get("is_default", False)

    def __repr__(self):
        tag = "DEFAULT" if self.is_default else "CONSENSUS"
        return f"<GovernanceDecision {tag} action={self.action}>"


# ──────────────────────────────────────────────
# Governance Context
# ──────────────────────────────────────────────

@dataclass
class GovernanceContext:
    active_contracts: List[Any] = field(default_factory=list)
    recent_history: List[GovernanceDecision] = field(default_factory=list)
    member_statuses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    identity_vector: Optional[List[float]] = None
    ontology: Optional[Any] = None

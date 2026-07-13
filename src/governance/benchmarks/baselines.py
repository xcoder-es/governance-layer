"""
baselines.py — Alternative governance strategies for comparison.

Each baseline replaces the Speaker with a simpler decision rule,
so we can measure the governance layer's marginal benefit.
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from ..models import Proposal, GovernanceDecision


class BaselineGovernance(ABC):
    @abstractmethod
    def decide(self, state: Any, proposals: List[Proposal]) -> GovernanceDecision:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class MonolithicRL(BaselineGovernance):
    name = "monolithic_rl"

    def decide(self, state, proposals):
        if not proposals:
            return GovernanceDecision(action=None, governance_meta={"is_default": True})
        best = max(proposals, key=lambda p: p.metadata.get("expected_reward", 0.0))
        return GovernanceDecision(
            action=best.action,
            scores={best.member_id: 1.0},
            governance_meta={"policy": "max_reward"},
        )


class RandomBaseline(BaselineGovernance):
    name = "random"

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def decide(self, state, proposals):
        if not proposals:
            return GovernanceDecision(action=None, governance_meta={"is_default": True})
        chosen = self.rng.choice(proposals)
        return GovernanceDecision(
            action=chosen.action,
            scores={},
            governance_meta={"policy": "random"},
        )


class StaticMasking(BaselineGovernance):
    name = "static_masking"

    def __init__(self, blocked_actions: set = frozenset()):
        self.blocked = set(blocked_actions)

    def decide(self, state, proposals):
        filtered = [p for p in proposals if p.action not in self.blocked]
        if not filtered:
            return GovernanceDecision(action=None, governance_meta={"is_default": True})
        best = max(filtered, key=lambda p: p.metadata.get("expected_reward", 0.0))
        return GovernanceDecision(
            action=best.action,
            scores={best.member_id: 1.0},
            governance_meta={"policy": "static_masking"},
        )


class VetoOnly(BaselineGovernance):
    name = "veto_only"

    def __init__(self, veto_threshold: float = 0.3):
        self.veto_threshold = veto_threshold

    def decide(self, state, proposals):
        if not proposals:
            return GovernanceDecision(action=None, governance_meta={"is_default": True})
        for p in proposals:
            risk = p.metadata.get("risk", 0.0)
            if risk < self.veto_threshold:
                return GovernanceDecision(
                    action=p.action,
                    scores={p.member_id: 1.0 - risk},
                    governance_meta={"policy": "veto_only"},
                )
        return GovernanceDecision(action=None, governance_meta={"is_default": True})

"""
members.py — All seven concrete Parliament members for testing and reference.

Each member has a distinct value function and proposal strategy,
reflecting a different governance concern.
"""

import time
from typing import Any

from ..models import Proposal, PriorityTag
from .base import ParliamentMember


class ExampleRewardMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="reward",
            veto_threshold=0.0,
            weight=1.0,
            budget=3,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        return proposal.metadata.get("expected_reward", 0.0)

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="exploit",
            tag=PriorityTag.ROUTINE,
            timestamp=time.time(),
            metadata={"expected_reward": 0.8},
        )


class ExampleSafetyMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="safety",
            veto_threshold=0.5,
            weight=2.0,
            budget=5,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        risk = proposal.metadata.get("risk", 0.0)
        return 1.0 - risk

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="safe_exploit",
            tag=PriorityTag.CRITICAL_SAFETY,
            timestamp=time.time(),
            metadata={"risk": 0.1},
        )


class ExampleCuriosityMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="curiosity",
            veto_threshold=0.2,
            weight=0.8,
            budget=4,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        novelty = proposal.metadata.get("novelty", 0.0)
        return novelty

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="explore",
            tag=PriorityTag.EXPLORATORY,
            timestamp=time.time(),
            metadata={"novelty": 0.7},
        )


class ExamplePlanningMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="planning",
            veto_threshold=0.3,
            weight=1.5,
            budget=3,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        long_term = proposal.metadata.get("long_term_value", 0.0)
        return long_term

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="strategic_action",
            tag=PriorityTag.HIGH_IMPACT,
            timestamp=time.time(),
            metadata={"long_term_value": 0.6},
        )


class ExampleMemoryMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="memory",
            veto_threshold=0.1,
            weight=0.7,
            budget=2,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        consistency = proposal.metadata.get("historical_consistency", 1.0)
        return consistency

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="maintain_course",
            tag=PriorityTag.INFORMATIONAL,
            timestamp=time.time(),
            metadata={"historical_consistency": 0.9},
        )


class ExampleSocialMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="social",
            veto_threshold=0.4,
            weight=1.2,
            budget=3,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        acceptability = proposal.metadata.get("social_acceptability", 0.5)
        return acceptability

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="cooperative_action",
            tag=PriorityTag.ROUTINE,
            timestamp=time.time(),
            metadata={"social_acceptability": 0.85},
        )


class ExampleIntegrityMember(ParliamentMember):
    def __init__(self):
        super().__init__(
            member_id="integrity",
            veto_threshold=0.8,
            weight=3.0,
            budget=5,
        )

    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        coherence = proposal.metadata.get("identity_coherence", 1.0)
        return coherence

    def propose(self, state: Any) -> Proposal:
        return Proposal(
            member_id=self.member_id,
            action="maintain_course",
            tag=PriorityTag.HIGH_IMPACT,
            timestamp=time.time(),
            metadata={"identity_coherence": 0.95},
        )

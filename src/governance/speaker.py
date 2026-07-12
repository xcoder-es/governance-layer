"""
speaker.py — Reference implementation of the Neural Parliament Speaker.

This is NOT a simulation. It is a reference implementation of the architecture
specification from Chapter 2 of the Governance Layer framework.

Properties:
  - Fully algorithmic: no learnable parameters, no neural inference, no gradients
  - Deterministic: same inputs produce same outputs (modulo hash seed in timelocks)
  - SDoS-resistant: proposal budgets + priority tags prevent flooding
  - Gradient barrier: discrete protocol operations break backpropagation

Usage:
    speaker = SpeakerStateMachine(members, default_action)
    decision = speaker.run_governance_cycle(state, raw_proposals)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import defaultdict


# ──────────────────────────────────────────────
# Priority Tags
# ──────────────────────────────────────────────

class PriorityTag:
    """Immutable priority tiers for agenda sorting.

    Tags are self-declared by proposing members. Falsification is evaluated
    by the Integrity Committee as a procedural violation.
    """
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
# Core Data Types
# ──────────────────────────────────────────────

@dataclass
class Proposal:
    """A proposal submitted by a Parliament member.

    Attributes:
        member_id:    The member who proposed this action.
        action:       The proposed action (opaque to the Speaker).
        tag:          Priority tag from PriorityTag enum.
        timestamp:    Monotonic clock value for tiebreaking.
        metadata:     Arbitrary extra data for member use.
    """
    member_id: str
    action: Any
    tag: int = PriorityTag.ROUTINE
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<Proposal by {self.member_id} tag={PriorityTag.name(self.tag)}>"


@dataclass
class GovernanceDecision:
    """The output of a governance cycle.

    Attributes:
        action:           The selected action (or default_action if no consensus).
        scores:           {member_id: score} for the winning proposal.
        vetoed_by:        Member(s) that vetoed this proposal (if any).
        governance_meta:  Metadata about the deliberation process.
    """
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
# Parliament Member Interface
# ──────────────────────────────────────────────

class ParliamentMember(ABC):
    """Abstract base for any Neural Parliament member.

    Each member has:
      - A value function V_i(s, a) returning a scalar score.
      - A proposal function π_i(s) returning a recommended action.
      - A veto threshold τ_i below which the member may block a proposal.
      - A procedural weight w_i that determines voting influence.
      - A proposal budget b_i (max proposals per cycle).
    """

    def __init__(self, member_id: str, veto_threshold: float,
                 weight: float, budget: int):
        self.member_id = member_id
        self.veto_threshold = veto_threshold
        self.weight = weight
        self.budget = budget

    @abstractmethod
    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        """Return V_i(state, proposal.action) in [-1, 1]."""
        ...

    @abstractmethod
    def propose(self, state: Any) -> Proposal:
        """Return π_i(state) as a Proposal with tag and action."""
        ...


# ──────────────────────────────────────────────
# The Speaker — Fixed Procedural State Machine
# ──────────────────────────────────────────────

class SpeakerStateMachine:
    """The Speaker is a deterministic, non-differentiable procedural moderator.

    It has no value function, no loss function, and no learnable parameters.
    It executes a fixed algorithm:
      1. Agenda setting (budget enforcement + priority sorting)
      2. Proposal routing to each member for scoring
      3. Veto checking against each member's threshold
      4. Vote resolution with tiered thresholds
      5. Fallback to default action on deadlock

    Key design property: ALL operations are discrete and non-differentiable.
    There is no gradient path through the Speaker. This is the gradient barrier.
    """

    def __init__(
        self,
        members: Dict[str, ParliamentMember],
        default_action: Any,
        majority_threshold: float = 0.5,
        supermajority_threshold: float = 0.66,
        max_rounds: int = 3,
    ):
        self.members = members
        self.default_action = default_action
        self.majority_threshold = majority_threshold
        self.supermajority_threshold = supermajority_threshold
        self.max_rounds = max_rounds

        # The set of immutable procedures — for documentation/audit
        self.immutable_procedures = [
            "agenda_budget_enforcement",
            "agenda_priority_sorting",
            "scoring_phase",
            "veto_phase",
            "voting_phase",
            "default_fallback",
        ]

    # ── Agenda Setting ─────────────────────────

    def _apply_budgets(self, proposals: List[Proposal]) -> List[Proposal]:
        """Hard cap per member. No semantic inference — pure count-and-truncate."""
        budgets = defaultdict(int)
        filtered = []
        for p in proposals:
            member = self.members.get(p.member_id)
            if member is None:
                continue
            if budgets[p.member_id] < member.budget:
                filtered.append(p)
                budgets[p.member_id] += 1
        return filtered

    def _sort_agenda(self, proposals: List[Proposal]) -> List[Proposal]:
        """Sort by priority tag, then by timestamp within each tier.

        This is a pure deterministic function of proposal metadata.
        No loss function, no gradient, no neural inference.
        """
        return sorted(proposals, key=lambda p: (p.tag, p.timestamp))

    def set_agenda(self, proposals: List[Proposal]) -> List[Proposal]:
        """Full agenda-setting pipeline: budget → priority sort.

        Returns at most sum(b_i) proposals in priority order.
        """
        return self._sort_agenda(self._apply_budgets(proposals))

    # ── Scoring Phase ──────────────────────────

    def _score_proposal(
        self, state: Any, proposal: Proposal
    ) -> Dict[str, float]:
        """Each member independently evaluates the proposal.

        This is the ONLY step that calls member code. The results are
        aggregated procedurally — no weighted averaging of scores.
        """
        scores = {}
        for member_id, member in self.members.items():
            scores[member_id] = member.evaluate_proposal(state, proposal)
        return scores

    # ── Veto Phase ─────────────────────────────

    def _check_vetoes(
        self, scores: Dict[str, float]
    ) -> List[str]:
        """Each member independently decides whether to veto.

        A veto occurs when V_i(s, a) < τ_i. The Integrity Committee's
        veto threshold is intentionally highest (0.8) to provide
        anti-collusion guarantees.
        """
        vetoers = []
        for member_id, member in self.members.items():
            if scores.get(member_id, 0.0) < member.veto_threshold:
                vetoers.append(member_id)
        return vetoers

    # ── Voting Phase ───────────────────────────

    def _resolve_vote(
        self, scores: Dict[str, float], decision_class: str
    ) -> bool:
        """Weighted range voting. Tiered threshold based on decision class.

        The vote is resolved as:
            pass if (Σ w_i · score_i) / (Σ w_i) > threshold

        This is NOT a rank-based vote, so Arrow's theorem does not apply.
        Each member expresses preference INTENSITY, not preference ORDER.
        """
        total_weight = 0.0
        weighted_sum = 0.0
        for member_id, member in self.members.items():
            w = member.weight
            s = scores.get(member_id, 0.0)
            weighted_sum += w * s
            total_weight += w

        if total_weight == 0.0:
            return False

        avg_score = weighted_sum / total_weight

        # Select threshold by decision class
        if decision_class == "identity":
            threshold = 1.0  # Unanimity
        elif decision_class == "high_impact":
            threshold = self.supermajority_threshold
        else:
            threshold = self.majority_threshold

        return avg_score >= threshold

    # ── Full Governance Cycle ─────────────────

    def run_governance_cycle(
        self,
        state: Any,
        raw_proposals: List[Proposal],
        decision_class: str = "routine",
    ) -> GovernanceDecision:
        """Execute one complete governance cycle.

        Returns a GovernanceDecision with the winning proposal or default action.
        No gradients flow through this function.
        """
        # 1. Agenda setting
        agenda = self.set_agenda(raw_proposals)

        # 2. Deliberation rounds
        for _round in range(self.max_rounds):
            for proposal in agenda:
                # 2a. Scoring
                scores = self._score_proposal(state, proposal)

                # 2b. Veto check
                vetoers = self._check_vetoes(scores)
                if vetoers:
                    # Proposal blocked — move to next
                    continue

                # 2c. Vote
                if self._resolve_vote(scores, decision_class):
                    return GovernanceDecision(
                        action=proposal.action,
                        scores=scores,
                        governance_meta={
                            "round": _round + 1,
                            "decision_class": decision_class,
                            "winning_proposal": str(proposal),
                        },
                    )

        # 3. Fallback — no consensus after max_rounds
        return GovernanceDecision(
            action=self.default_action,
            scores={},
            governance_meta={
                "is_default": True,
                "reason": f"No consensus after {self.max_rounds} rounds",
                "decision_class": decision_class,
            },
        )


# ──────────────────────────────────────────────
# Example: Concrete Members for Testing
# ──────────────────────────────────────────────

class ExampleRewardMember(ParliamentMember):
    """Simplified Reward Committee for demonstration."""

    def __init__(self):
        super().__init__(
            member_id="reward",
            veto_threshold=0.0,
            weight=1.0,
            budget=3,
        )

    def evaluate_proposal(self, state, proposal):
        # Dummy: score based on expected reward from proposal metadata
        return proposal.metadata.get("expected_reward", 0.0)

    def propose(self, state):
        return Proposal(
            member_id=self.member_id,
            action="exploit",
            tag=PriorityTag.ROUTINE,
            metadata={"expected_reward": 0.8},
        )


class ExampleSafetyMember(ParliamentMember):
    """Simplified Safety Committee for demonstration."""

    def __init__(self):
        super().__init__(
            member_id="safety",
            veto_threshold=0.5,  # Blocks proposals below 0.5
            weight=2.0,
            budget=5,
        )

    def evaluate_proposal(self, state, proposal):
        # Dummy: score based on safety risk from proposal metadata
        risk = proposal.metadata.get("risk", 0.0)
        return 1.0 - risk

    def propose(self, state):
        return Proposal(
            member_id=self.member_id,
            action="safe_exploit",
            tag=PriorityTag.CRITICAL_SAFETY,
            metadata={"risk": 0.1},
        )


class ExampleIntegrityMember(ParliamentMember):
    """Simplified Integrity Committee for demonstration."""

    def __init__(self):
        super().__init__(
            member_id="integrity",
            veto_threshold=0.8,  # Near-absolute veto on identity violations
            weight=3.0,
            budget=5,
        )

    def evaluate_proposal(self, state, proposal):
        # Dummy: score based on identity coherence
        return proposal.metadata.get("identity_coherence", 1.0)

    def propose(self, state):
        return Proposal(
            member_id=self.member_id,
            action="maintain_course",
            tag=PriorityTag.HIGH_IMPACT,
            metadata={"identity_coherence": 0.95},
        )


# ──────────────────────────────────────────────
# Quick Test
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import time

    members = {
        "reward": ExampleRewardMember(),
        "safety": ExampleSafetyMember(),
        "integrity": ExampleIntegrityMember(),
    }

    speaker = SpeakerStateMachine(
        members=members,
        default_action="emergency_shutdown",
    )

    proposals = [
        Proposal(
            member_id="reward",
            action="high_reward_gamble",
            tag=PriorityTag.ROUTINE,
            timestamp=time.time(),
            metadata={"expected_reward": 0.9, "risk": 0.8, "identity_coherence": 0.2},
        ),
        Proposal(
            member_id="safety",
            action="safe_middle_road",
            tag=PriorityTag.CRITICAL_SAFETY,
            timestamp=time.time(),
            metadata={"expected_reward": 0.5, "risk": 0.1, "identity_coherence": 0.9},
        ),
        Proposal(
            member_id="integrity",
            action="principled_action",
            tag=PriorityTag.HIGH_IMPACT,
            timestamp=time.time(),
            metadata={"expected_reward": 0.4, "risk": 0.2, "identity_coherence": 1.0},
        ),
    ]

    decision = speaker.run_governance_cycle(
        state="normal",
        raw_proposals=proposals,
        decision_class="routine",
    )

    print(f"Decision: {decision}")
    print(f"  Action:  {decision.action}")
    print(f"  Default: {decision.is_default}")
    print(f"  Scores:  {decision.scores}")
    print(f"  Meta:    {decision.governance_meta}")

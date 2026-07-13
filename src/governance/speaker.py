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

from typing import Any, Dict, List
from collections import defaultdict

from .models import PriorityTag, Proposal, GovernanceDecision
from .committee.base import ParliamentMember


class SpeakerStateMachine:
    TAG_COMPLIANCE_THRESHOLD = 0.4
    FALSIFICATION_BUDGET_CUTOFF = 3

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
        self._falsification_counts: Dict[str, int] = {}
        self.immutable_procedures = [
            "agenda_budget_enforcement", "agenda_priority_sorting",
            "scoring_phase", "tag_compliance_check",
            "veto_phase", "voting_phase", "default_fallback",
        ]

    def _apply_budgets(self, proposals: List[Proposal]) -> List[Proposal]:
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
        return sorted(proposals, key=lambda p: (p.tag, p.timestamp))

    def set_agenda(self, proposals: List[Proposal]) -> List[Proposal]:
        return self._sort_agenda(self._apply_budgets(proposals))

    def _score_proposal(self, state: Any, proposal: Proposal) -> Dict[str, float]:
        scores = {}
        for member_id, member in self.members.items():
            scores[member_id] = member.evaluate_proposal(state, proposal)
        return scores

    def _check_tag_compliance(self, proposals: List[Proposal],
                              integrity_scores: Dict[str, float]) -> Dict[str, int]:
        for p in proposals:
            score = integrity_scores.get(p.member_id, 1.0)
            if score < self.TAG_COMPLIANCE_THRESHOLD:
                self._falsification_counts[p.member_id] = (
                    self._falsification_counts.get(p.member_id, 0) + 1
                )
        for member_id, count in self._falsification_counts.items():
            if count >= self.FALSIFICATION_BUDGET_CUTOFF:
                member = self.members.get(member_id)
                if member is not None:
                    member.budget = max(1, member.budget // 2)
        return dict(self._falsification_counts)

    def _check_vetoes(self, scores: Dict[str, float]) -> List[str]:
        vetoers = []
        for member_id, member in self.members.items():
            if scores.get(member_id, 0.0) < member.veto_threshold:
                vetoers.append(member_id)
        return vetoers

    def _resolve_vote(self, scores: Dict[str, float],
                      decision_class: str) -> bool:
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
        if decision_class == "identity":
            threshold = 1.0
        elif decision_class == "high_impact":
            threshold = self.supermajority_threshold
        else:
            threshold = self.majority_threshold
        return avg_score >= threshold

    def run_governance_cycle(
        self,
        state: Any,
        raw_proposals: List[Proposal],
        decision_class: str = "routine",
    ) -> GovernanceDecision:
        self._falsification_counts = {}
        agenda = self.set_agenda(raw_proposals)

        for _round in range(self.max_rounds):
            if _round == 0:
                integrity_scores = {}
                for p in agenda:
                    p_scores = self._score_proposal(state, p)
                    integrity_scores[p.member_id] = p_scores.get("integrity", 1.0)
                self._check_tag_compliance(agenda, integrity_scores)

            for proposal in agenda:
                scores = self._score_proposal(state, proposal)
                vetoers = self._check_vetoes(scores)
                if vetoers:
                    continue
                if self._resolve_vote(scores, decision_class):
                    return GovernanceDecision(
                        action=proposal.action,
                        scores=scores,
                        governance_meta={
                            "round": _round + 1,
                            "decision_class": decision_class,
                            "winning_proposal": str(proposal),
                            "falsification_counts": dict(self._falsification_counts),
                        },
                    )

        return GovernanceDecision(
            action=self.default_action,
            scores={},
            governance_meta={
                "is_default": True,
                "reason": f"No consensus after {self.max_rounds} rounds",
                "decision_class": decision_class,
                "falsification_counts": dict(self._falsification_counts),
            },
        )


# ──────────────────────────────────────────────
# Quick test runner for CLI use
# ──────────────────────────────────────────────


def _run_speaker_quick_test():
    import time
    from .committee.members import (
        ExampleRewardMember, ExampleSafetyMember, ExampleIntegrityMember,
    )

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


if __name__ == "__main__":
    _run_speaker_quick_test()

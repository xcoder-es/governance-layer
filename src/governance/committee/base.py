"""
base.py — Abstract base for Neural Parliament members.

Each member has:
  - A value function V_i(s, a) returning a scalar score in [-1, 1]
  - A proposal function pi_i(s) returning a recommended action
  - A veto threshold tau_i below which the member may block a proposal
  - A procedural weight w_i that determines voting influence
  - A proposal budget b_i (max proposals per cycle)
"""

from abc import ABC, abstractmethod
from typing import Any

from ..models import Proposal


class ParliamentMember(ABC):
    def __init__(self, member_id: str, veto_threshold: float,
                 weight: float, budget: int):
        self.member_id = member_id
        self.veto_threshold = veto_threshold
        self.weight = weight
        self.budget = budget

    @abstractmethod
    def evaluate_proposal(self, state: Any, proposal: Proposal) -> float:
        ...

    @abstractmethod
    def propose(self, state: Any) -> Proposal:
        ...

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.member_id} w={self.weight}>"

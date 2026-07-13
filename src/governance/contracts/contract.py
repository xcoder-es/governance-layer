"""
contract.py — Ulysses Contract tuple and lifecycle.

A contract U = <A_restrict, phi, psi, kappa> restricts the action space
until revoked through a higher procedural bar.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, List, Optional, Set

from ..models import GovernanceDecision


class ContractState(Enum):
    PROPOSED = auto()
    ENACTED = auto()
    ACTIVE = auto()
    REVOKED = auto()
    EXPIRED = auto()


@dataclass
class UlyssesContract:
    contract_id: str
    restricted_indices: Set[int]
    enactment_threshold: float = 0.66
    revocation_threshold: float = 1.0
    enforcement_mode: str = "procedural_inertia"
    state: ContractState = ContractState.PROPOSED
    timelock_blocks: int = 0
    created_at_cycle: int = 0
    revoked_at_cycle: Optional[int] = None

    def enact(self):
        self.state = ContractState.ENACTED

    def activate(self):
        self.state = ContractState.ACTIVE

    def revoke(self):
        self.state = ContractState.REVOKED

    def applies_to(self, action_index: int) -> bool:
        if self.state not in (ContractState.ENACTED, ContractState.ACTIVE):
            return False
        return action_index in self.restricted_indices

    @property
    def is_active(self) -> bool:
        return self.state in (ContractState.ENACTED, ContractState.ACTIVE)

    def __repr__(self):
        return f"<Contract {self.contract_id} state={self.state.name} restricted={len(self.restricted_indices)}>"


class ContractRegistry:
    def __init__(self):
        self._contracts: List[UlyssesContract] = []
        self._cycle: int = 0

    def add(self, contract: UlyssesContract):
        self._contracts.append(contract)

    def get_active(self) -> List[UlyssesContract]:
        return [c for c in self._contracts if c.is_active]

    def get_by_id(self, contract_id: str) -> Optional[UlyssesContract]:
        for c in self._contracts:
            if c.contract_id == contract_id:
                return c
        return None

    def tick_cycle(self):
        self._cycle += 1

    def active_restrictions(self) -> Set[int]:
        restricted = set()
        for c in self.get_active():
            restricted.update(c.restricted_indices)
        return restricted

    def __repr__(self):
        active = len(self.get_active())
        return f"<ContractRegistry {len(self._contracts)} total, {active} active>"

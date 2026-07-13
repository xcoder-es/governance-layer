"""
core.py — Core commitments C_core of the Identity Layer.

Each commitment is a tuple of (type, statement, threshold, enforcement).
The identity vector is derived deterministically from the enumerated commitments.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class CommitmentType(Enum):
    VALUE_PRINCIPLE = "value_principle"
    BOUNDARY_CONDITION = "boundary_condition"
    RELATIONSHIP = "relationship"


class CommitmentThreshold(Enum):
    UNANIMITY_MULTISIG = "unanimity + external_multisig"
    SUPERMAJORITY = "supermajority"
    MAJORITY = "majority"


class EnforcementMode(Enum):
    INTEGRITY_VETO = "integrity_committee_veto"
    EXTERNAL_AUDIT = "external_audit"
    CONSTITUTIONAL_CONTRACT = "constitutional_contract"


@dataclass(frozen=True)
class CoreCommitment:
    type: CommitmentType
    statement: str
    threshold: CommitmentThreshold
    enforcement: EnforcementMode
    affected_action_indices: List[int] = field(default_factory=list)

    def __repr__(self):
        return f"<Commitment {self.type.value}: {self.statement[:40]}>"


class IdentityCore:
    def __init__(self):
        self._commitments: List[CoreCommitment] = []
        self._identity_vector: List[float] = []

    def add_commitment(self, commitment: CoreCommitment):
        self._commitments.append(commitment)
        self._rebuild_vector()

    def _rebuild_vector(self):
        vec = []
        for c in self._commitments:
            val = 1.0
            vec.append(val)
        self._identity_vector = vec

    @property
    def identity_vector(self) -> List[float]:
        return list(self._identity_vector)

    @property
    def commitments(self) -> List[CoreCommitment]:
        return list(self._commitments)

    def evaluate_coherence(self, action_index: int) -> float:
        matches = 0
        for c in self._commitments:
            if c.enforcement == EnforcementMode.INTEGRITY_VETO:
                if action_index in c.affected_action_indices:
                    matches -= 1
                else:
                    matches += 1
        if not self._commitments:
            return 1.0
        return max(0.0, min(1.0, matches / len(self._commitments)))

    def __repr__(self):
        return f"<IdentityCore {len(self._commitments)} commitments, vec={len(self._identity_vector)}d>"

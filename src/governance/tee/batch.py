"""
batch.py — Merkle-tree batch verification for TEE throughput.

The optimization layer submits a batch root hash; the TEE validates
the macro-trajectory; the optimizer executes individual actions
with Merkle proofs.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class BatchProposal:
    action_indices: List[int]
    aggregate_risk: float = 0.0
    diversity_score: float = 1.0
    batch_metadata: Dict[str, Any] = field(default_factory=dict)


def merkle_root(items: List[bytes]) -> str:
    if not items:
        return hashlib.sha256(b"empty").hexdigest()
    if len(items) == 1:
        return hashlib.sha256(items[0]).hexdigest()
    mid = len(items) // 2
    left = merkle_root(items[:mid])
    right = merkle_root(items[mid:])
    combined = (left + right).encode()
    return hashlib.sha256(combined).hexdigest()


def compute_diversity(action_indices: List[int]) -> float:
    if not action_indices:
        return 1.0
    unique = len(set(action_indices))
    return unique / len(action_indices)


class BatchVerifier:
    def __init__(self, risk_threshold: float = 0.7,
                 diversity_min: float = 0.3):
        self.risk_threshold = risk_threshold
        self.diversity_min = diversity_min

    def validate_batch(self, proposal: BatchProposal) -> Tuple[bool, str]:
        if proposal.aggregate_risk > self.risk_threshold:
            return False, (
                f"Aggregate risk {proposal.aggregate_risk:.2f} exceeds "
                f"threshold {self.risk_threshold}"
            )
        div = compute_diversity(proposal.action_indices)
        if div < self.diversity_min:
            return False, (
                f"Diversity {div:.2f} below minimum {self.diversity_min}"
            )
        root = merkle_root([str(i).encode() for i in proposal.action_indices])
        return True, f"Batch valid. Root: {root[:16]}..."

    def verify_proof(self, action_index: int, proof: List[str],
                     root: str) -> bool:
        current = hashlib.sha256(str(action_index).encode()).hexdigest()
        for sibling in proof:
            combined = "".join(sorted([current, sibling]))
            current = hashlib.sha256(combined.encode()).hexdigest()
        return current == root

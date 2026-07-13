"""
ontology.py — Formal action namespace with runtime integrity hashes.

The ontology O binds each action index to its operational semantics
and a runtime integrity hash. The TEE verifies at batch validation time
that the current runtime implementation matches the genesis commitment.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class ActionBinding:
    index: int
    operation: str
    runtime_hash: str
    properties: Dict[str, float]


def compute_hash(implementation_bytes: bytes) -> str:
    return hashlib.sha256(implementation_bytes).hexdigest()


class Ontology:
    def __init__(self):
        self._bindings: Dict[int, ActionBinding] = {}
        self._append_only_log: List[ActionBinding] = []

    def register(self, index: int, operation: str,
                 implementation_bytes: bytes,
                 properties: Dict[str, float]) -> ActionBinding:
        if index in self._bindings:
            raise ValueError(f"Action index {index} already bound")
        h = compute_hash(implementation_bytes)
        binding = ActionBinding(
            index=index,
            operation=operation,
            runtime_hash=h,
            properties=properties,
        )
        self._bindings[index] = binding
        self._append_only_log.append(binding)
        return binding

    def verify_binding(self, index: int,
                       runtime_implementation: bytes) -> bool:
        if index not in self._bindings:
            return False
        expected = self._bindings[index].runtime_hash
        actual = compute_hash(runtime_implementation)
        return actual == expected

    def get_properties(self, index: int) -> Optional[Dict[str, float]]:
        binding = self._bindings.get(index)
        if binding is None:
            return None
        return dict(binding.properties)

    def has_index(self, index: int) -> bool:
        return index in self._bindings

    @property
    def size(self) -> int:
        return len(self._bindings)

    def __repr__(self):
        return f"<Ontology {self.size} actions>"

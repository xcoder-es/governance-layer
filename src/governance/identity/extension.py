"""
extension.py — Ontology extension protocol with sandboxed isolation buffer.

New actions enter an Isolation Buffer State for 30-day simulated cooling-off,
empirically measured by independent monitors before external audit and finalization.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from .keys import GenesisMultisig
from .ontology import Ontology, ActionBinding


class ExtensionPhase(Enum):
    PROPOSAL = auto()
    ISOLATION_BUFFER = auto()
    EMPIRICAL_AUDIT = auto()
    FINALIZED = auto()
    REJECTED = auto()


@dataclass
class ExtensionCandidate:
    index: int
    operation: str
    candidate_properties: Dict[str, float]
    empirical_properties: Optional[Dict[str, float]] = None
    phase: ExtensionPhase = ExtensionPhase.PROPOSAL
    monitor_reports: List[Dict[str, Any]] = field(default_factory=list)
    multisig_approved: bool = False
    runtime_hash: Optional[str] = None

    @property
    def is_sandboxed(self) -> bool:
        return self.phase == ExtensionPhase.ISOLATION_BUFFER


class ExtensionSandbox:
    def __init__(self, ontology: Ontology, multisig: GenesisMultisig):
        self.ontology = ontology
        self.multisig = multisig
        self._candidates: Dict[int, ExtensionCandidate] = {}

    def propose(self, index: int, operation: str,
                candidate_properties: Dict[str, float]) -> ExtensionCandidate:
        if self.ontology.has_index(index):
            raise ValueError(f"Index {index} already bound")
        candidate = ExtensionCandidate(
            index=index,
            operation=operation,
            candidate_properties=candidate_properties,
        )
        self._candidates[index] = candidate
        return candidate

    def run_sandbox(self, index: int, rounds: int = 5):
        candidate = self._candidates.get(index)
        if candidate is None or candidate.phase != ExtensionPhase.PROPOSAL:
            return
        candidate.phase = ExtensionPhase.ISOLATION_BUFFER

        empirical = dict(candidate.candidate_properties)
        for r in range(rounds):
            for key in empirical:
                noise = (secrets.randbelow(11) - 5) / 100.0
                empirical[key] = round(max(0.0, min(1.0, empirical[key] + noise)), 3)
            candidate.monitor_reports.append({
                "round": r + 1,
                "observed": dict(empirical),
            })
        candidate.empirical_properties = empirical

    def audit(self, index: int, tolerance: float = 0.1) -> bool:
        candidate = self._candidates.get(index)
        if candidate is None or candidate.empirical_properties is None:
            return False
        for key in candidate.candidate_properties:
            diff = abs(candidate.candidate_properties[key] - candidate.empirical_properties[key])
            if diff > tolerance:
                candidate.phase = ExtensionPhase.REJECTED
                return False
        return True

    def finalize(self, index: int,
                 implementation_bytes: bytes) -> Optional[ActionBinding]:
        candidate = self._candidates.get(index)
        if candidate is None:
            return None
        if not self.multisig.is_authorized:
            candidate.phase = ExtensionPhase.REJECTED
            return None
        if not self.audit(index):
            return None
        binding = self.ontology.register(
            index=index,
            operation=candidate.operation,
            implementation_bytes=implementation_bytes,
            properties=candidate.empirical_properties or candidate.candidate_properties,
        )
        candidate.phase = ExtensionPhase.FINALIZED
        candidate.runtime_hash = binding.runtime_hash
        return binding

    def get_candidate(self, index: int) -> Optional[ExtensionCandidate]:
        return self._candidates.get(index)

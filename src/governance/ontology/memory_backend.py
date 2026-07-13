"""
memory_backend.py — In-memory implementation of OntologyBackend.

Used by default. No external dependencies. Data is ephemeral.
"""

import hashlib
import secrets
from typing import Any, Dict, List, Optional, Tuple

from .backend import OntologyBackend


class MemoryBackend(OntologyBackend):
    def __init__(self):
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relationships: List[Tuple[str, str, str]] = []
        self._identity_vector: List[float] = []

    def _generate_id(self) -> str:
        return hashlib.sha256(secrets.token_bytes(16)).hexdigest()[:12]

    def add_entity(self, type_: str, properties: Dict[str, Any]) -> str:
        eid = self._generate_id()
        self._entities[eid] = {"id": eid, "type": type_, **properties}
        return eid

    def add_relationship(self, from_id: str, to_id: str, relation: str) -> bool:
        if from_id not in self._entities or to_id not in self._entities:
            return False
        self._relationships.append((from_id, to_id, relation))
        return True

    def query_relationships(self, entity_id: str) -> List[Tuple[str, str, str]]:
        results = []
        for f, t, r in self._relationships:
            if f == entity_id:
                results.append((t, r, "outgoing"))
            if t == entity_id:
                results.append((f, r, "incoming"))
        return results

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self._entities.get(entity_id)

    def get_entities_by_type(self, type_: str) -> List[Dict[str, Any]]:
        return [e for e in self._entities.values() if e.get("type") == type_]

    def get_identity_vector(self) -> List[float]:
        return list(self._identity_vector)

    def set_identity_vector(self, vector: List[float]):
        self._identity_vector = list(vector)

    def close(self):
        self._entities.clear()
        self._relationships.clear()

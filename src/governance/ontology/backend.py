"""
backend.py — Abstract interface for ontology storage.

Two implementations:
  - MemoryBackend: in-memory dicts (no deps, default)
  - Neo4jBackend: Cypher queries to Neo4j Aura

Governance code never imports Neo4j directly. It only talks to this ABC.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class OntologyBackend(ABC):
    @abstractmethod
    def add_entity(self, type_: str, properties: Dict[str, Any]) -> str:
        ...

    @abstractmethod
    def add_relationship(self, from_id: str, to_id: str, relation: str) -> bool:
        ...

    @abstractmethod
    def query_relationships(self, entity_id: str) -> List[Tuple[str, str, str]]:
        ...

    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_entities_by_type(self, type_: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_identity_vector(self) -> List[float]:
        ...

    @abstractmethod
    def set_identity_vector(self, vector: List[float]):
        ...

    @abstractmethod
    def close(self):
        ...

"""
keys.py — Key hierarchy and simulated 3-of-5 multisig for genesis bootstrapping.

The TEE holds the root key material. Identity signing keys require
external multisig (t-of-n) to activate.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KeyHolder:
    name: str
    public_key: str
    has_signed: bool = False


class GenesisMultisig:
    def __init__(self, threshold: int = 3, total_holders: int = 5):
        self.threshold = threshold
        self.holders: List[KeyHolder] = []

    def add_holder(self, name: str) -> str:
        pk = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]
        self.holders.append(KeyHolder(name=name, public_key=pk))
        return pk

    def sign(self, holder_name: str) -> bool:
        for h in self.holders:
            if h.name == holder_name and not h.has_signed:
                h.has_signed = True
                return True
        return False

    @property
    def signatures_count(self) -> int:
        return sum(1 for h in self.holders if h.has_signed)

    @property
    def is_authorized(self) -> bool:
        return self.signatures_count >= self.threshold

    def reset(self):
        for h in self.holders:
            h.has_signed = False


@dataclass
class GenesisManifest:
    ontology_hash: str = ""
    core_commitments_hash: str = ""
    parameter_envelope_hash: str = ""
    member_set_hash: str = ""
    multisig: GenesisMultisig = field(default_factory=GenesisMultisig)
    is_sealed: bool = False

    def seal(self):
        self.is_sealed = True

    def __repr__(self):
        return f"<GenesisManifest sealed={self.is_sealed} sigs={self.multisig.signatures_count}/{self.multisig.threshold}>"

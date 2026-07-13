"""
enclave.py — Simulated TEE enclave with sealing, attestation, isolated memory.

The enclave provides hardware-level guarantees in software for testing.
In production, this would run inside SGX/SEV/TrustZone.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..identity.keys import GenesisManifest


@dataclass
class AttestationReport:
    enclave_hash: str
    is_debug: bool
    sealed_data_hash: str
    valid: bool = True


class SimulatedEnclave:
    def __init__(self, genesis: Optional[GenesisManifest] = None):
        self._genesis = genesis
        self._sealed_storage: Dict[str, Any] = {}
        self._measurement = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        self._attested = False

    def attest(self) -> AttestationReport:
        self._attested = True
        sealed_hash = hashlib.sha256(
            str(self._sealed_storage).encode()
        ).hexdigest()
        return AttestationReport(
            enclave_hash=self._measurement,
            is_debug=False,
            sealed_data_hash=sealed_hash,
        )

    def seal(self, key: str, value: Any):
        self._sealed_storage[key] = value

    def unseal(self, key: str) -> Optional[Any]:
        return self._sealed_storage.get(key)

    def verify_measurement(self, expected_hash: str) -> bool:
        return self._measurement == expected_hash

    @property
    def is_attested(self) -> bool:
        return self._attested

    def cold_boot(self, genesis: GenesisManifest):
        self._genesis = genesis
        self._sealed_storage = {}
        self._measurement = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        self._attested = False

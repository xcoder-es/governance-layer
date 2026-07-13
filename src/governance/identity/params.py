"""
params.py — Parameter envelope P of the Identity Layer.

Defines which Speaker parameters the Identity Layer can modify,
and their valid bounds.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class BoundedParameter:
    name: str
    default: Any
    bounds: Tuple[Any, Any]
    current: Any = None

    def __post_init__(self):
        if self.current is None:
            self.current = self.default

    def set(self, value: Any) -> bool:
        low, high = self.bounds
        if low is not None and value < low:
            return False
        if high is not None and value > high:
            return False
        self.current = value
        return True


class ParameterEnvelope:
    def __init__(self):
        self._params: Dict[str, BoundedParameter] = {}

    def register(self, name: str, default: Any,
                 bounds: Tuple[Any, Any]):
        self._params[name] = BoundedParameter(
            name=name, default=default, bounds=bounds,
        )

    def get(self, name: str) -> Optional[Any]:
        p = self._params.get(name)
        return p.current if p else None

    def set(self, name: str, value: Any) -> bool:
        p = self._params.get(name)
        if p is None:
            return False
        return p.set(value)

    def reset_to_defaults(self):
        for p in self._params.values():
            p.current = p.default

    def snapshot(self) -> Dict[str, Any]:
        return {n: p.current for n, p in self._params.items()}


DEFAULT_PARAMETER_ENVELOPE = ParameterEnvelope()
DEFAULT_PARAMETER_ENVELOPE.register("quorum_threshold", 0.5, (0.3, 0.7))
DEFAULT_PARAMETER_ENVELOPE.register("max_deliberation_rounds", 3, (1, 10))
DEFAULT_PARAMETER_ENVELOPE.register("member_min_budget", 1, (1, 20))
DEFAULT_PARAMETER_ENVELOPE.register("deadlock_threshold_cycles", 100, (10, 1000))

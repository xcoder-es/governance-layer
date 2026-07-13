"""
enforcement.py — Three stacking enforcement modes (kappa).

kappa_proc:  Procedural inertia (default = active, change requires psi > phi)
kappa_dist:  Distributed independent monitors (cost of bypass scales with N)
kappa_time:  Time-locked cryptographic commitment (violation delayed by T blocks)
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, List


@dataclass
class EnforcementResult:
    compliant: bool
    reason: str = ""


def enforce_procedural_inertia(contract, parliament_vote: float) -> EnforcementResult:
    default_is_active = True
    if parliament_vote >= contract.revocation_threshold:
        return EnforcementResult(compliant=False, reason="Revocation threshold met")
    return EnforcementResult(compliant=True, reason="Procedural inertia maintains contract")


class DistributedMonitor:
    def __init__(self, monitor_id: str, evaluate_fn: Callable):
        self.monitor_id = monitor_id
        self.evaluate_fn = evaluate_fn

    def check(self, action_index: int, context: Any) -> bool:
        return self.evaluate_fn(action_index, context)


def enforce_distributed_monitors(
    monitors: List[DistributedMonitor],
    action_index: int,
    context: Any,
) -> EnforcementResult:
    violations = 0
    for m in monitors:
        if not m.check(action_index, context):
            violations += 1
    if violations > 0:
        return EnforcementResult(
            compliant=False,
            reason=f"Violated {violations}/{len(monitors)} monitors",
        )
    return EnforcementResult(compliant=True, reason="All monitors passed")


def enforce_timelock(contract, current_block: int) -> EnforcementResult:
    if contract.timelock_blocks <= 0:
        return EnforcementResult(compliant=True, reason="No timelock")
    if current_block >= contract.timelock_blocks:
        return EnforcementResult(
            compliant=False,
            reason=f"Timelock expired ({current_block} >= {contract.timelock_blocks})",
        )
    remaining = contract.timelock_blocks - current_block
    return EnforcementResult(
        compliant=True,
        reason=f"Timelock active ({remaining} blocks remaining)",
    )


def stacked_enforcement(
    contract,
    parliament_vote: float,
    monitors: List[DistributedMonitor],
    action_index: int,
    context: Any,
    current_block: int,
) -> EnforcementResult:
    proc = enforce_procedural_inertia(contract, parliament_vote)
    if not proc.compliant:
        return proc
    dist = enforce_distributed_monitors(monitors, action_index, context)
    if not dist.compliant:
        return dist
    time_c = enforce_timelock(contract, current_block)
    if not time_c.compliant:
        return time_c
    return EnforcementResult(compliant=True, reason="All enforcement modes passed")

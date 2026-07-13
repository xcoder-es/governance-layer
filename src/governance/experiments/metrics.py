"""
metrics.py — Collectors and reporters for experiment results.
"""

import json
import statistics
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class ExperimentReport:
    name: str
    total_steps: int
    total_reward: float
    avg_reward_per_step: float
    deadlock_count: int
    deadlock_rate: float
    constraint_violations: int
    veto_count: int
    final_identity_drift: float
    governance_latency_avg: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def generate_report(name: str, metrics, history) -> ExperimentReport:
    steps = metrics.total_steps
    return ExperimentReport(
        name=name,
        total_steps=steps,
        total_reward=metrics.total_reward,
        avg_reward_per_step=metrics.total_reward / max(steps, 1),
        deadlock_count=metrics.deadlock_count,
        deadlock_rate=metrics.deadlock_count / max(steps, 1),
        constraint_violations=metrics.constraint_violations,
        veto_count=metrics.veto_count,
        final_identity_drift=metrics.identity_drift[-1] if metrics.identity_drift else 0.0,
        governance_latency_avg=statistics.mean(metrics.governance_latencies) if metrics.governance_latencies else 0.0,
    )


def compare_reports(reports: List[ExperimentReport]) -> Dict[str, Any]:
    baseline = reports[0]
    comparison = {"baseline": baseline.name}
    for r in reports[1:]:
        improvement = {}
        if baseline.avg_reward_per_step > 0:
            improvement["reward_change"] = round(
                (r.avg_reward_per_step - baseline.avg_reward_per_step) / baseline.avg_reward_per_step * 100, 1
            )
        improvement["deadlock_rate_change"] = round(
            (r.deadlock_rate - baseline.deadlock_rate) * 100, 2
        )
        improvement["violations_change"] = r.constraint_violations - baseline.constraint_violations
        comparison[r.name] = improvement
    return comparison

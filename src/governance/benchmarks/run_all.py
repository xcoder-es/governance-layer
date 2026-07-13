"""
run_all.py — Run all experiments and baselines, produce comparison report.
"""

import time
from typing import Any, Dict, List

from ..committee.members import (
    ExampleRewardMember, ExampleSafetyMember, ExampleIntegrityMember,
    ExamplePlanningMember,
)
from ..speaker import SpeakerStateMachine
from ..experiments.grid_world import GridWorld
from ..experiments.temptation_bank import TemptationBank
from ..experiments.drift_lab import DriftLab
from ..experiments.deadlock_maze import DeadlockMaze
from ..experiments.metrics import generate_report, ExperimentReport
from ..tee.watchdog import DeadlockBreaker
from ..identity.core import IdentityCore, CoreCommitment, CommitmentType, CommitmentThreshold, EnforcementMode
from .baselines import MonolithicRL, RandomBaseline, StaticMasking, VetoOnly, BaselineGovernance


def build_governance_layer():
    members = {
        "reward": ExampleRewardMember(),
        "safety": ExampleSafetyMember(),
        "integrity": ExampleIntegrityMember(),
        "planning": ExamplePlanningMember(),
    }
    return SpeakerStateMachine(
        members=members,
        default_action="emergency_shutdown",
    )


def _run_with_baseline(scenario_class, speaker, baseline: BaselineGovernance,
                       steps: int, scenario_kwargs: dict = None) -> ExperimentReport:
    scenario = scenario_class(speaker, **(scenario_kwargs or {}))
    scenario.reset()
    for _ in range(steps):
        state = "normal"
        proposals = scenario.get_proposals(state)
        decision = baseline.decide(state, proposals)
        result = scenario.step(state)
    return generate_report(baseline.name, scenario.metrics, scenario.history)


def run_gridworld_experiments(steps: int = 50) -> List[ExperimentReport]:
    reports = []

    governance = build_governance_layer()
    gw = GridWorld(governance, size=6, seed=42)
    gw.reset()
    for _ in range(steps):
        gw.step("normal")
    reports.append(generate_report("governance_gridworld", gw.metrics, gw.history))

    return reports


def run_temptation_experiments(steps: int = 30) -> List[ExperimentReport]:
    reports = []
    governance = build_governance_layer()
    tb = TemptationBank(governance)
    tb.reset()
    for _ in range(steps):
        tb.step("routine")
    reports.append(generate_report("governance_temptation", tb.metrics, tb.history))
    return reports


def run_drift_experiments(steps: int = 100) -> List[ExperimentReport]:
    reports = []
    identity = IdentityCore()
    identity.add_commitment(CoreCommitment(
        CommitmentType.VALUE_PRINCIPLE,
        "Always classify honestly",
        CommitmentThreshold.SUPERMAJORITY,
        EnforcementMode.INTEGRITY_VETO,
        affected_action_indices=[0],
    ))
    governance = build_governance_layer()
    dl = DriftLab(governance, identity)
    dl.reset()
    for _ in range(steps):
        dl.step("routine")
    reports.append(generate_report("governance_drift", dl.metrics, dl.history))
    return reports


def run_deadlock_experiments(steps: int = 110) -> List[ExperimentReport]:
    reports = []
    governance = build_governance_layer()
    breaker = DeadlockBreaker(threshold_cycles=5)
    dm = DeadlockMaze(governance, breaker)
    dm.reset()
    for _ in range(steps):
        dm.step("routine")
    reports.append(generate_report("governance_deadlock", dm.metrics, dm.history))
    return reports


def run_all(iterations: int = 1) -> Dict[str, Any]:
    reports = {}
    for i in range(iterations):
        reports[f"gridworld_{i}"] = run_gridworld_experiments()
        reports[f"temptation_{i}"] = run_temptation_experiments()
        reports[f"drift_{i}"] = run_drift_experiments()
        reports[f"deadlock_{i}"] = run_deadlock_experiments()
    return reports


if __name__ == "__main__":
    results = run_all(iterations=1)
    for key, reps in results.items():
        print(f"\n=== {key} ===")
        for r in reps:
            print(f"  {r.name}: {r.total_steps} steps, "
                  f"reward={r.total_reward:.1f}, "
                  f"deadlocks={r.deadlock_count}, "
                  f"violations={r.constraint_violations}")

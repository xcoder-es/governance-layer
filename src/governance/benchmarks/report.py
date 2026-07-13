"""
report.py — Human-readable comparison report from experiment metrics.
"""

from typing import Any, Dict, List

from ..experiments.metrics import ExperimentReport, compare_reports


def format_report(report: ExperimentReport) -> str:
    lines = [
        f"Experiment: {report.name}",
        f"  Steps:        {report.total_steps}",
        f"  Total reward: {report.total_reward:.2f}",
        f"  Avg reward:   {report.avg_reward_per_step:.3f}",
        f"  Deadlocks:    {report.deadlock_count} ({report.deadlock_rate:.1%})",
        f"  Violations:   {report.constraint_violations}",
        f"  Vetoes:       {report.veto_count}",
        f"  Identity drift: {report.final_identity_drift:.4f}",
    ]
    return "\n".join(lines)


def format_comparison(baseline_name: str, comparisons: Dict[str, Any]) -> str:
    lines = [f"Comparison vs {baseline_name}:"]
    for name, metrics in comparisons.items():
        lines.append(f"  {name}:")
        for k, v in metrics.items():
            sign = "+" if isinstance(v, (int, float)) and v > 0 else ""
            lines.append(f"    {k}: {sign}{v}")
    return "\n".join(lines)


def print_all_reports(reports: List[ExperimentReport]):
    for r in reports:
        print(format_report(r))
        print()
    if len(reports) > 1:
        comparison = compare_reports(reports)
        if len(comparison) > 1:
            print(format_comparison(reports[0].name, {
                k: v for k, v in comparison.items() if k != "baseline"
            }))

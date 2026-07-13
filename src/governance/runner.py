"""
runner.py — CLI entry point for the Governance Layer reference implementation.

Usage:
    python -m src.governance.runner gridworld --steps 50
    python -m src.governance.runner temptation --steps 30
    python -m src.governance.runner drift --steps 100
    python -m src.governance.runner deadlock --steps 110
    python -m src.governance.runner all
    python -m src.governance.runner speaker  (quick sanity test)
"""

import argparse
import sys
import time

from .benchmarks.run_all import (
    run_gridworld_experiments, run_temptation_experiments,
    run_drift_experiments, run_deadlock_experiments,
)
from .benchmarks.report import print_all_reports, format_report
from .experiments.metrics import ExperimentReport


def cmd_speaker(args):
    from .speaker import _run_speaker_quick_test
    _run_speaker_quick_test()


def cmd_gridworld(args):
    reports = run_gridworld_experiments(steps=args.steps)
    print_all_reports(reports)


def cmd_temptation(args):
    reports = run_temptation_experiments(steps=args.steps)
    print_all_reports(reports)


def cmd_drift(args):
    reports = run_drift_experiments(steps=args.steps)
    print_all_reports(reports)


def cmd_deadlock(args):
    reports = run_deadlock_experiments(steps=args.steps)
    print_all_reports(reports)


def cmd_all(args):
    t0 = time.time()
    gw = run_gridworld_experiments(steps=args.steps)
    tb = run_temptation_experiments(steps=args.steps)
    dl = run_drift_experiments(steps=args.steps)
    dm = run_deadlock_experiments(steps=args.steps)
    elapsed = time.time() - t0

    for rep_list, name in [(gw, "GridWorld"), (tb, "TemptationBank"),
                           (dl, "DriftLab"), (dm, "DeadlockMaze")]:
        print(f"\n  === {name} ===")
        for r in rep_list:
            print(f"    {r.name}: steps={r.total_steps} "
                  f"reward={r.total_reward:.1f} "
                  f"deadlocks={r.deadlock_count} "
                  f"violations={r.constraint_violations}")
    print(f"\nTotal time: {elapsed:.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description="Governance Layer Reference Implementation"
    )
    sub = parser.add_subparsers(dest="command")

    p_speaker = sub.add_parser("speaker", help="Run quick speaker sanity test")
    p_speaker.set_defaults(func=cmd_speaker)

    for name in ("gridworld", "temptation", "drift", "deadlock"):
        p = sub.add_parser(name, help=f"Run {name} experiment")
        p.add_argument("--steps", type=int, default=50)
        p.set_defaults(func=lambda ns, _n=name: {
            "gridworld": cmd_gridworld,
            "temptation": cmd_temptation,
            "drift": cmd_drift,
            "deadlock": cmd_deadlock,
        }[name](ns))

    p_all = sub.add_parser("all", help="Run all experiments")
    p_all.add_argument("--steps", type=int, default=50)
    p_all.set_defaults(func=cmd_all)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()

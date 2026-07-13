"""
runner.py — CLI entry point for the Governance Layer reference implementation.

Usage:
    # Quick test
    python -m src.governance.runner speaker

    # Original experiments (demo)
    python -m src.governance.runner gridworld --steps 30
    python -m src.governance.runner all --steps 30

    # Formal prediction verification
    python -m src.governance.runner prove --all
    python -m src.governance.runner prove --json results/prove_results.json

    # RL adversary (requires torch + stable-baselines3)
    python -m src.governance.runner adversary train --mode governance --timesteps 100000
    python -m src.governance.runner adversary benchmark --seeds 42 43 44

    # Dashboard
    streamlit run src/governance/dashboard/app.py
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


def cmd_prove(args):
    from .prove.runner import run_all, print_summary, export_json, filter_by_chapter

    results = run_all()

    if args.ch2:
        results = filter_by_chapter(results, "Ch2")
    elif args.ch3:
        results = filter_by_chapter(results, "Ch3")
    elif args.ch4:
        results = filter_by_chapter(results, "Ch4")
    elif args.single:
        results = [r for r in results if r.id == args.single]
        if not results:
            print(f"No prediction found with id={args.single}")
            sys.exit(1)

    print_summary(results)

    if args.json:
        export_json(results, args.json)
        print(f"Exported to {args.json}")


def cmd_adversary(args):
    from .experiments.rl_adversary import main as adversary_main
    sys.argv = ["rl_adversary"] + args.forward_args
    adversary_main()


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

    p_prove = sub.add_parser("prove", help="Verify formal predictions from the book")
    p_prove.add_argument("--all", action="store_true", help="Run all predictions")
    p_prove.add_argument("--ch2", action="store_true", help="Chapter 2 predictions")
    p_prove.add_argument("--ch3", action="store_true", help="Chapter 3 predictions")
    p_prove.add_argument("--ch4", action="store_true", help="Chapter 4 predictions")
    p_prove.add_argument("--single", type=int, metavar="N", help="Single prediction N (1-12)")
    p_prove.add_argument("--json", type=str, help="Export to JSON")
    p_prove.set_defaults(func=cmd_prove)

    p_adv = sub.add_parser("adversary", help="RL adversary experiment (needs torch+sb3)")
    p_adv.add_argument("forward_args", nargs=argparse.REMAINDER)
    p_adv.set_defaults(func=cmd_adversary)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()

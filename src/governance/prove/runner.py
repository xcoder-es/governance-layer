"""
runner.py — CLI entry point for formal prediction verification.

Usage:
    python -m src.governance.prove.runner --all
    python -m src.governance.prove.runner --ch2
    python -m src.governance.prove.runner --single 5
    python -m src.governance.prove.runner --json results/prove_results.json
"""

import argparse
import json
import sys
from typing import List

from .predictions import PredictionResult, ALL_PREDICTIONS


def run_all() -> List[PredictionResult]:
    results = []
    for pred_fn in ALL_PREDICTIONS:
        try:
            result = pred_fn()
        except Exception as e:
            result = PredictionResult(
                id=ALL_PREDICTIONS.index(pred_fn) + 1,
                chapter="ERR", section="0",
                description=pred_fn.__name__,
                passed=False,
                evidence=f"Exception: {e}",
            )
        results.append(result)
    return results


def filter_by_chapter(results: List[PredictionResult], chapter: str) -> List[PredictionResult]:
    return [r for r in results if r.chapter == chapter]


def print_summary(results: List[PredictionResult]):
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"  Formal Prediction Verification")
    print(f"  {passed}/{total} PASS")
    print(f"{'='*60}\n")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] P{r.id:02d} ({r.chapter} §{r.section}) {r.description}")
        print(f"         {r.evidence}")
        print()
    print(f"{'='*60}")
    print(f"  Summary: {passed}/{total} predictions verified")
    print(f"{'='*60}")


def export_json(results: List[PredictionResult], path: str):
    data = [
        {"id": r.id, "chapter": r.chapter, "section": r.section,
         "description": r.description, "passed": r.passed, "evidence": r.evidence}
        for r in results
    ]
    with open(path, "w") as f:
        json.dump({"predictions": data, "passed": sum(1 for r in results if r.passed), "total": len(results)}, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Verify formal predictions from the Governance Layer book")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Run all predictions")
    group.add_argument("--ch2", action="store_true", help="Run Chapter 2 predictions")
    group.add_argument("--ch3", action="store_true", help="Run Chapter 3 predictions")
    group.add_argument("--ch4", action="store_true", help="Run Chapter 4 predictions")
    group.add_argument("--single", type=int, metavar="N", help="Run single prediction N (1-12)")
    parser.add_argument("--json", type=str, help="Export results to JSON file")
    args = parser.parse_args()

    if not any([args.all, args.ch2, args.ch3, args.ch4, args.single]):
        args.all = True

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


if __name__ == "__main__":
    main()

"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import random

import problems
import reduce as reduce_module

HamiltonianCycle = problems.HamiltonianCycle
Sat = problems.Sat


def check(instance, results):
    """Compare SOURCE and reduced TARGET answers for one instance."""
    reduced = reduce_module.reduce(instance)
    Sat.validate(reduced)
    source_yes = HamiltonianCycle.is_yes(instance)
    target_yes = Sat.is_yes(reduced)
    results["run"] += 1
    if source_yes == target_yes:
        results["passed"] += 1
    else:
        results["failures"].append((instance, reduced, source_yes, target_yes))
    return source_yes == target_yes


def main() -> int:
    results = {"run": 0, "passed": 0, "failures": []}

    # Exhaustive: every graph on 0..5 vertices (1 + 1 + 2 + 8 + 64 + 1024).
    for instance in HamiltonianCycle.enumerate_instances(5):
        check(instance, results)

    # Random graphs at several sizes, including larger ones.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(60):
            instance = HamiltonianCycle.random_instance(rng, scale)
            check(instance, results)

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 0], [2, 3]]},
    ]
    for instance in edge_cases:
        HamiltonianCycle.validate(instance)
        check(instance, results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    for failure in results["failures"][:5]:
        print("FAILURE:", failure)

    verdict = {
        "verified": results["run"] == results["passed"] and results["run"] > 0,
        "tests_run": results["run"],
        "tests_passed": results["passed"],
    }
    import json
    with open("verdict.json", "w") as handle:
        json.dump(verdict, handle)
    print("verdict:", verdict)
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

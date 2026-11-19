"""Tests for the Clique -> Vertex Cover reduction in reduce.py."""

import random

import problems
from reduce import reduce

SOURCE = problems.SOURCE
TARGET = problems.TARGET


def check(instance):
    """Return True iff source and reduced target agree; also validate."""
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    return SOURCE.is_yes(instance) == TARGET.is_yes(out)


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def record(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ok = check(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, repr(exc)))
            return
        if ok:
            tests_passed += 1
        else:
            failures.append((label, inst, "mismatch"))

    # 1. Exhaustive small instances (all graphs up to scale 4, all k).
    for inst in SOURCE.enumerate_instances(4):
        record(inst, "enumerate")

    # 2. Random instances across scales.
    rng = random.Random(12345)
    for scale in range(0, 8):
        for _ in range(200):
            record(SOURCE.random_instance(rng, scale), "random")

    # 3. Hand-crafted edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 3},        # empty graph, clique of 1 only
        {"n": 3, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},  # complete
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},  # k > n
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": -3},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},          # two disjoint edges
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 3},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 2},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 1},
        {"n": 2, "edges": [[0, 1]], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        # reversed edge order should behave the same
        {"n": 3, "edges": [[1, 0], [2, 1]], "k": 2},
    ]
    for inst in edge_cases:
        record(inst, "edge_case")

    # 4. Larger random instances to stress the construction.
    rng2 = random.Random(999)
    for scale in range(8, 13):
        for _ in range(50):
            record(SOURCE.random_instance(rng2, scale), "random_large")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, why in failures[:10]:
            print(" ", label, inst, why)

    verified = tests_run > 0 and tests_passed == tests_run
    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())

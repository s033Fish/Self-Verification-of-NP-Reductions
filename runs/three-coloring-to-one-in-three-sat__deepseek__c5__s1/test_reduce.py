"""Independent tests for reduce.py (3-Coloring -> 1-in-3-SAT).

We compare our own brute-force solvers on many small source instances and
their reductions, and we also validate the produced target instances.
"""

from __future__ import annotations

import itertools
import sys

from brute import solve_one_in_three, solve_three_coloring
from problems import OneInThreeSat, ThreeColoring
from reduce import reduce

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    label = repr(instance)
    try:
        ThreeColoring.validate(instance)
    except Exception as exc:  # source instance must be valid
        failures.append(f"source invalid {label}: {exc}")
        return
    try:
        target = reduce(instance)
    except Exception as exc:
        failures.append(f"reduce raised on {label}: {exc!r}")
        return
    try:
        OneInThreeSat.validate(target)
    except Exception as exc:
        failures.append(f"target invalid for {label}: {exc} -> {target!r}")
        return
    expected = solve_three_coloring(instance)
    got = solve_one_in_three(target)
    if expected != got:
        failures.append(
            f"MISMATCH {label}: source={expected} target={got} target_inst={target!r}"
        )
        return
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main() -> int:
    # Exhaustive over all simple graphs with up to 6 vertices.
    for n in range(0, 7):
        for g in all_graphs(n):
            check(g)

    # A few larger / structured graphs to exercise the construction more.
    structured = [
        {"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]]},
        {"n": 8, "edges": [[i, j] for i in range(8) for j in range(i + 1, 8)]},  # K8
        {"n": 9, "edges": [[i, (i + 1) % 9] for i in range(9)]},  # C9
        {"n": 10, "edges": [[i, j] for i in range(5) for j in range(5, 10)]},  # K5,5
        {"n": 12, "edges": [[i, (i + 1) % 12] for i in range(12)]},  # C12
    ]
    for g in structured:
        check(g)


    # Randomized stress tests on somewhat larger graphs.
    import random
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        p = rng.choice([0.2, 0.4, 0.6, 0.8])
        edges = [list(pr) for pr in pairs if rng.random() < p]
        check({"n": n, "edges": edges})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  " + f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

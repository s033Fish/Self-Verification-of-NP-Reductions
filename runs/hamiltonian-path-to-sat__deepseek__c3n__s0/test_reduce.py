"""Tests for reduce.py: compare brute-force answers on source instances
with brute-force answers on their reductions."""

from __future__ import annotations

import itertools

import problems
from reduce import reduce
from solvers import solve_hamiltonian_path, solve_sat

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    problems.HamiltonianPath.validate(instance)
    out = reduce(instance)
    problems.Sat.validate(out)
    expected = solve_hamiltonian_path(instance)
    got = solve_sat(out)
    if expected != got:
        raise AssertionError(
            f"MISMATCH on {instance}: source={expected}, target={got}, reduction={out}"
        )
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask >> k & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    # n = 0 and n = 1 edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})

    # Exhaustive over all graphs for n = 2, 3, 4, 5.
    for n in range(2, 6):
        for g in all_graphs(n):
            check(g)

    # A few larger random-ish structured cases (n = 6, 7) to stress the
    # encoding beyond exhaustive enumeration.
    import random

    rng = random.Random(12345)
    for n in (6, 7):
        for _ in range(300):
            pairs = list(itertools.combinations(range(n), 2))
            edges = [list(p) for p in pairs if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8])]
            check({"n": n, "edges": edges})
        # guaranteed Hamiltonian path 0-1-...-(n-1)
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        # complete graph
        check({"n": n, "edges": [list(p) for p in itertools.combinations(range(n), 2)]})
        # empty graph
        check({"n": n, "edges": []})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

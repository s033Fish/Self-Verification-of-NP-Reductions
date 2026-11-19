"""Compare brute-force Clique answers with SAT answers on reductions."""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat
from reduce import reduce
from solvers import solve_clique, solve_sat, solve_sat_dpll

tests_run = 0
tests_passed = 0


def check(instance, sat_solver):
    global tests_run, tests_passed
    tests_run += 1
    Clique.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = solve_clique(instance)
    got = sat_solver(out)
    assert got == expected, (
        f"mismatch on {instance}: clique={expected}, sat={got}, reduction={out}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for idx, p in enumerate(pairs) if (mask >> idx) & 1]
        yield edges


def main():
    # Exhaustive small graphs, all k including edge cases.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                if k * n <= 14:
                    check({"n": n, "edges": edges, "k": k}, solve_sat)
                else:
                    check({"n": n, "edges": edges, "k": k}, solve_sat_dpll)

    # Random larger instances (DPLL to keep runtime sane).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 2)
        check({"n": n, "edges": edges, "k": k}, solve_sat_dpll)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

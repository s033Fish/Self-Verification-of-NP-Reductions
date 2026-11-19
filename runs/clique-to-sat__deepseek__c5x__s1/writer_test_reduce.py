"""Tests for reduce.py: Clique -> SAT.

Contains solvers for both problems (problems.py has none) and compares
solver answers on many small random Clique instances with the answers of
their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_clique(instance: dict) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause (DPLL backtracking)."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    if any(len(c) == 0 for c in clauses):
        return False

    def simplify(clauses, var, value):
        """Apply var=value, return simplified clause list or None if conflict."""
        out = []
        for clause in clauses:
            if (var if value else -var) in clause:
                continue  # clause already satisfied
            reduced = tuple(l for l in clause if l != (-var if value else var))
            if not reduced:
                return None  # empty clause -> conflict
            out.append(reduced)
        return out

    def dpll(clauses):
        if not clauses:
            return True
        # unit propagation
        for clause in clauses:
            if len(clause) == 1:
                lit = clause[0]
                new = simplify(clauses, abs(lit), lit > 0)
                if new is None:
                    return False
                return dpll(new)
        # choose a variable from the first clause
        var = abs(clauses[0][0])
        for value in (True, False):
            new = simplify(clauses, var, value)
            if new is not None and dpll(new):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Random instance generation (small, so solving is feasible).

def random_clique_instance(rng: random.Random, max_n: int = 5) -> dict:
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in all_pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Hand-picked edge cases first.
    hand_cases = [
        {"n": 0, "edges": [], "k": 0},      # k <= 0 -> yes
        {"n": 0, "edges": [], "k": -5},     # k <= 0 -> yes
        {"n": 0, "edges": [], "k": 1},      # k > n  -> no
        {"n": 1, "edges": [], "k": 1},      # yes
        {"n": 1, "edges": [], "k": 2},      # no
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},  # triangle -> yes
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},          # path -> no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 4},  # K4 -> yes
        {"n": 5, "edges": [], "k": 2},      # no
        {"n": 5, "edges": [], "k": 0},      # yes
        {"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)], "k": 6},  # K6 -> yes
        {"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)], "k": 7},  # k>n -> no
    ]

    cases = list(hand_cases)
    for _ in range(1500):
        cases.append(random_clique_instance(rng))

    for instance in cases:
        Clique.validate(instance)
        expected = solve_clique(instance)

        target = reduce(instance)
        Sat.validate(target)  # reduction must produce a valid SAT instance
        got = solve_sat(target)

        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("  instance:", instance)
            print("  clique answer:", expected)
            print("  reduced :", target)
            print("  sat answer   :", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()

"""Tests for reduce.py: brute-force solvers + randomized equivalence checks."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, ExactCover
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_sat(instance: dict) -> bool:
    """Brute force: try all assignments of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Backtracking exact cover: repeatedly cover the lowest uncovered element."""
    u = instance["universe_size"]
    target = (1 << u) - 1

    masks = set()
    for s in instance["sets"]:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.add(mask)
    masks = list(masks)

    # sets containing each element
    by_elem = [[] for _ in range(u)]
    for mask in masks:
        for e in range(u):
            if mask >> e & 1:
                by_elem[e].append(mask)

    def rec(covered: int) -> bool:
        if covered == target:
            return True
        # lowest uncovered element
        e = 0
        while covered >> e & 1:
            e += 1
        for mask in by_elem[e]:
            if mask & covered == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ---------------------------------------------------------------- generators

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
    m = rng.randint(0, max_vars)
    q = rng.randint(0, max_clauses)
    if q > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(q):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ---------------------------------------------------------------- tests

def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -3], [-1, -2, 3]]},
    ]

    instances = list(fixed)
    for _ in range(600):
        instances.append(random_three_sat(rng))

    for inst in instances:
        ThreeSat.validate(inst)
        out = reduce(inst)
        ExactCover.validate(out)

        expected = solve_three_sat(inst)
        got = solve_exact_cover(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH:", inst, "expected", expected, "got", got, "reduction", out)

    # structural sanity: sizes are polynomial (linear) in the input
    for inst in instances:
        out = reduce(inst)
        assert out["universe_size"] == inst["num_vars"] + 4 * len(inst["clauses"])
        assert len(out["sets"]) == 2 * inst["num_vars"] + 6 * len(inst["clauses"])

    return tests_run, tests_passed


if __name__ == "__main__":
    tr, tp = run_tests()
    print(f"tests_run={tr} tests_passed={tp}")
    assert tr == tp, "some tests failed"
    print("ALL TESTS PASSED")

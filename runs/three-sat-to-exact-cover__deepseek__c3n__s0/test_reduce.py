"""Brute-force solvers for both problems plus tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_three_sat(instance: dict) -> bool:
    """Try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # variable v (1-based) -> bits[v-1]
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
    full = (1 << u) - 1
    masks = set()
    for s in instance["sets"]:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask:
            masks.add(mask)
    masks = list(masks)
    # For each element, the sets that contain it.
    by_elem = [[] for _ in range(u)]
    for mask in masks:
        for e in range(u):
            if mask >> e & 1:
                by_elem[e].append(mask)

    def bt(covered: int) -> bool:
        if covered == full:
            return True
        # lowest uncovered element
        e = 0
        while covered >> e & 1:
            e += 1
        for mask in by_elem[e]:
            if mask & covered:
                continue
            if bt(covered | mask):
                return True
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generators (small, valid instances).
# ----------------------------------------------------------------------

def gen_random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        n = rng.randint(0, max_clauses)
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_three_sat_instances(max_vars: int = 4, max_clauses: int = 3):
    """Exhaustively enumerate small valid 3-SAT instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        # All possible clauses over variables 1..m (3 distinct vars, any signs).
        possible = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product((1, -1), repeat=3):
                possible.append([s * v for s, v in zip(signs, vs)])
        for n in range(0, max_clauses + 1):
            for combo in itertools.combinations(possible, n):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check(instance: dict) -> bool:
    """Validate both instances and compare answers."""
    ThreeSat.validate(instance)
    target = reduce(instance)
    ExactCover.validate(target)
    src = solve_three_sat(instance)
    tgt = solve_exact_cover(target)
    assert src == tgt, (instance, target, src, tgt)
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive small instances.
    for instance in all_three_sat_instances(max_vars=4, max_clauses=2):
        tests_run += 1
        check(instance)
        tests_passed += 1

    # 2. Random instances, including larger variable counts.
    rng = random.Random(12345)
    for _ in range(2000):
        instance = gen_random_three_sat(rng, max_vars=6, max_clauses=6)
        tests_run += 1
        check(instance)
        tests_passed += 1

    # 3. Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 2, 3], [-4, -2, -3]]},
        # Unused variables.
        {"num_vars": 6, "clauses": [[1, 2, 3]]},
        # Duplicate clauses.
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        check(instance)
        tests_passed += 1

    # 4. Known unsatisfiable / satisfiable checks.
    unsat = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                        [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]}
    tests_run += 1
    assert solve_three_sat(unsat) is False
    assert solve_exact_cover(reduce(unsat)) is False
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

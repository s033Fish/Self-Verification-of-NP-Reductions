"""Brute-force solvers and randomized tests for the 1-in-3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_one_in_three_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(1 for v in clause if bits[v - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    # Deduplicate sets as bitmasks (empty sets are irrelevant).
    masks = []
    seen = set()
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask == 0:
            continue
        if mask not in seen:
            seen.add(mask)
            masks.append(mask)

    # Backtracking: cover the lowest uncovered element.
    def rec(covered: int) -> bool:
        if covered == full:
            return True
        # lowest uncovered element
        rest = (~covered) & full
        low = rest & (-rest)
        for mask in masks:
            if mask & low and not (mask & covered):
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ---------------------------------------------------------------- tests

def random_instance(rng, max_vars=5, max_clauses=4):
    m = rng.randint(0, max_vars)
    c = rng.randint(0, max_clauses)
    if c > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(c):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append(vs)
    return {"num_vars": m, "clauses": clauses}


def run():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Hand-picked edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 1]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [1, 4, 5]]},
    ]

    instances = list(fixed)
    for _ in range(400):
        instances.append(random_instance(rng))

    for inst in instances:
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        out = reduce(inst)
        ExactCover.validate(out)
        got = solve_exact_cover(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, "reduced", out)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    run()

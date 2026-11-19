"""Brute-force solvers and randomized tests for the 1-in-3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import random
import sys

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_1in3(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        good = True
        for clause in clauses:
            cnt = 0
            for v in clause:
                if (mask >> (v - 1)) & 1:
                    cnt += 1
            if cnt != 1:
                good = False
                break
        if good:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    sys.setrecursionlimit(10000)

    def rec(covered: int) -> bool:
        if covered == full:
            return True
        rem = full & ~covered
        e = (rem & -rem).bit_length() - 1  # lowest uncovered element
        for mask in masks:
            if (mask >> e) & 1 and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance generation

def random_instance(rng: random.Random) -> dict:
    m = rng.randint(0, 6)
    if m < 3:
        n = 0
    else:
        n = rng.randint(0, 4)
    clauses = []
    for _ in range(n):
        vars_ = rng.sample(range(1, m + 1), 3)
        rng.shuffle(vars_)
        clauses.append(vars_)
    # occasionally duplicate a clause
    if clauses and rng.random() < 0.3:
        clauses.append(list(rng.choice(clauses)))
    rng.shuffle(clauses)
    return {"num_vars": m, "clauses": clauses}


def main() -> int:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    # exhaustive-ish small deterministic cases plus random ones
    instances = []
    # no clauses, various m
    for m in range(0, 7):
        instances.append({"num_vars": m, "clauses": []})
    # single clause
    for m in range(3, 7):
        instances.append({"num_vars": m, "clauses": [[1, 2, 3]]})
    # duplicate clause
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    instances.append({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})
    # random
    for _ in range(400):
        instances.append(random_instance(rng))

    for inst in instances:
        OneInThreeSat.validate(inst)
        reduced = reduce(inst)
        ExactCover.validate(reduced)
        expected = solve_1in3(inst)
        got = solve_exact_cover(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, reduced, expected, got))

    if failures:
        print(f"FAILED {len(failures)} tests")
        for inst, reduced, expected, got in failures[:5]:
            print("source:", inst)
            print("target:", reduced)
            print("expected", expected, "got", got)
        return 1

    print(f"All {tests_passed}/{tests_run} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

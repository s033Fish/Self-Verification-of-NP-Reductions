"""Brute-force solvers and tests for the 3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)


def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        # bits[i] is the value of variable i+1
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """True iff some sub-collection of sets exactly covers the universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    target = (1 << u) - 1
    # Deduplicate: identical sets are interchangeable, so keeping one copy
    # preserves solvability.
    unique = list({tuple(sorted(s)) for s in sets})
    masks = []
    for s in unique:
        mask = 0
        for x in s:
            mask |= 1 << x
        masks.append(mask)
    # Simple backtracking / subset search with pruning.
    masks = [m for m in masks if m != 0]  # empty sets never matter
    masks.sort(key=lambda m: bin(m).count("1"), reverse=True)

    def search(idx: int, covered: int) -> bool:
        if covered == target:
            return True
        if idx == len(masks):
            return False
        # Prune: remaining sets can't help if we already passed them.
        for i in range(idx, len(masks)):
            m = masks[i]
            if m & covered:
                continue
            if search(i + 1, covered | m):
                return True
        return False

    return search(0, 0)


# ----------------------------------------------------------------------
# Instance generators


def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 6):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        nclauses = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustive small instances: m in 0..3, all clause subsets of a few clauses."""
    # m = 0,1,2 -> no clauses possible (a clause needs 3 distinct vars)
    for m in range(0, 3):
        yield {"num_vars": m, "clauses": []}
    # m = 3: enumerate subsets of all 8 clauses (2^3 sign choices) up to size 3
    m = 3
    all_clauses = [
        [s1 * 1, s2 * 2, s3 * 3]
        for s1 in (1, -1)
        for s2 in (1, -1)
        for s3 in (1, -1)
    ]
    for size in range(0, 4):
        for combo in itertools.combinations(all_clauses, size):
            yield {"num_vars": m, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Tests


def check(instance: dict, results: list):
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    ExactCover.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_exact_cover(reduced)
    results.append(expected == got)
    if expected != got:
        print("MISMATCH!")
        print("source:", instance)
        print("expected:", expected, "got:", got)
        print("reduced:", reduced)


def main():
    results: list = []

    # Exhaustive small cases.
    for inst in all_small_three_sat():
        check(inst, results)

    # Randomized cases.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_three_sat(rng)
        check(inst, results)

    # A few hand-crafted edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [-2, -3, 4]]},
    ]
    for inst in edge:
        check(inst, results)

    total = len(results)
    passed = sum(results)
    print(f"tests_run={total} tests_passed={passed}")
    assert passed == total, "some tests failed"

    # Write verdict.json.
    import json

    with open("verdict.json", "w") as fh:
        json.dump({"verified": passed == total, "tests_run": total, "tests_passed": passed}, fh)
    print("verdict.json written")


if __name__ == "__main__":
    main()

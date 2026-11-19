"""Tests for reduce.py: compare brute-force answers on source instances and
their reductions, then write verdict.json."""

from __future__ import annotations

import json
import random

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three(instance: dict) -> bool:
    """Try every assignment; yes iff every clause has exactly one true var."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << num_vars):
        good = True
        for a, b, c in clauses:
            count = ((mask >> (a - 1)) & 1) + ((mask >> (b - 1)) & 1) + ((mask >> (c - 1)) & 1)
            if count != 1:
                good = False
                break
        if good:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Backtracking exact cover: cover every element exactly once."""
    universe = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    full = (1 << universe) - 1

    def rec(covered: int) -> bool:
        if covered == full:
            return True
        remaining = full & ~covered
        # lowest uncovered element
        elem = (remaining & -remaining).bit_length() - 1
        for s in sets:
            mask = 0
            for x in s:
                mask |= 1 << x
            if (mask >> elem) & 1 and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance generation.

def random_instance(rng: random.Random, max_vars: int = 6, max_clauses: int = 6) -> dict:
    num_vars = rng.randint(0, max_vars)
    clauses: list[list[int]] = []
    if num_vars >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(rng.sample(range(1, num_vars + 1), 3))
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures: list[str] = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both instances must be valid.
        OneInThreeSat.validate(instance)
        reduced = reduce(instance)
        ExactCover.validate(reduced)
        expected = solve_one_in_three(instance)
        got = solve_exact_cover(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(f"{label}: source={instance} expected={expected} got={got} reduced={reduced}")

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "no clauses m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}, "two clauses")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]}, "four clauses")
    # Variable 5 never appears.
    check({"num_vars": 5, "clauses": [[1, 2, 3]]}, "unused variable")

    # Random tests.
    for i in range(3000):
        inst = random_instance(rng)
        check(inst, f"random#{i}")

    # Random tests with more clauses (denser, more likely unsat).
    for i in range(2000):
        inst = random_instance(rng, max_vars=5, max_clauses=12)
        check(inst, f"dense#{i}")

    verified = not failures
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
        fh.write("\n")

    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(" ", f)
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

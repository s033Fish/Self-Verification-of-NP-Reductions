"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_sat(instance: dict) -> bool:
    """Brute force over all assignments."""
    n = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=n):
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


def _subset_sums(numbers):
    sums = {0}
    for number in numbers:
        sums |= {s + number for s in sums}
    return sums


def solve_subset_sum(instance: dict) -> bool:
    """Exact meet-in-the-middle solver (handles huge values)."""
    target = instance["target"]
    if target < 0:
        return False
    numbers = instance["numbers"]
    mid = len(numbers) // 2
    left = _subset_sums(numbers[:mid])
    right = _subset_sums(numbers[mid:])
    return any(target - a in right for a in left)


# ---------------------------------------------------------------- generators

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5) -> dict:
    n = rng.randint(0, max_vars)
    if n < 3:
        clauses = []
    else:
        k = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(k):
            vs = rng.sample(range(1, n + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": n, "clauses": clauses}


def all_small_three_sat():
    """Exhaustive small instances: up to 4 vars, all clause combos of size <= 2."""
    for n in range(0, 5):
        if n < 3:
            yield {"num_vars": n, "clauses": []}
            continue
        # all possible clauses
        all_clauses = []
        for vs in itertools.combinations(range(1, n + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([v * s for v, s in zip(vs, signs)])
        # no clauses
        yield {"num_vars": n, "clauses": []}
        # single clauses
        for c in all_clauses:
            yield {"num_vars": n, "clauses": [c]}
        # pairs of clauses
        for c1, c2 in itertools.combinations(all_clauses, 2):
            yield {"num_vars": n, "clauses": [c1, c2]}


# ---------------------------------------------------------------- tests

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        expected = solve_three_sat(inst)
        got = solve_subset_sum(out)
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "expected", expected, "got", got, "reduction", out)

    # exhaustive small
    for inst in all_small_three_sat():
        check(inst)

    # exhaustive triples of clauses for n=3 (all 8 clauses over 3 vars)
    n = 3
    all_clauses = []
    for vs in itertools.combinations(range(1, n + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([v * s for v, s in zip(vs, signs)])
    for combo in itertools.combinations_with_replacement(all_clauses, 3):
        check({"num_vars": n, "clauses": list(combo)})

    # random larger
    rng = random.Random(12345)
    for _ in range(400):
        check(random_three_sat(rng, max_vars=6, max_clauses=8))
    for _ in range(80):
        check(random_three_sat(rng, max_vars=9, max_clauses=12))
    for _ in range(20):
        check(random_three_sat(rng, max_vars=12, max_clauses=15))

    # edge cases explicitly
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 10, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, 2, -3], [-1, -2, 3]]})
    # oracle counterexample: all 8 clauses over 3 vars -> unsatisfiable
    check({
        "num_vars": 3,
        "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
        ],
    })

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()

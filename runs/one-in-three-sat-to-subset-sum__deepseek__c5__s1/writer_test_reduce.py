"""Brute-force solvers for both problems and randomized tests of reduce.py."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(1 for var in clause if bits[var - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def _subset_sums(numbers):
    sums = {0}
    for a in numbers:
        sums |= {s + a for s in sums}
    return sums


def solve_subset_sum(instance) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # meet-in-the-middle (numbers can be huge, so no bitset DP)
    half = len(numbers) // 2
    left = _subset_sums(numbers[:half])
    right = _subset_sums(numbers[half:])
    return any((target - s) in right for s in left)


# ----------------------------------------------------------------------
# Random instance generation
# ----------------------------------------------------------------------

def random_instance(rng: random.Random):
    m = rng.randint(0, 7)
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = rng.randint(0, 8)
    clauses = []
    for _ in range(num_clauses):
        clause = rng.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Edge cases explicitly.
    edge_instances = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
    ]

    instances = edge_instances + [random_instance(rng) for _ in range(3000)]
    # larger instances with many clauses
    for _ in range(1500):
        m = rng.randint(3, 9)
        nc = rng.randint(0, 25)
        instances.append({"num_vars": m,
                          "clauses": [rng.sample(range(1, m + 1), 3)
                                      for _ in range(nc)]})

    for inst in instances:
        tests_run += 1
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        got = solve_subset_sum(out)
        assert got == expected, (inst, out, expected, got)
        tests_passed += 1

    # Also verify the reduction on all instances with m in {0,3,4} and all
    # possible clause multisets up to size 3, to be thorough.
    exhaustive = 0
    for m in (0, 3, 4):
        vars_ = list(range(1, m + 1))
        possible = list(itertools.combinations(vars_, 3)) if m >= 3 else []
        for size in range(0, 4):
            for combo in itertools.combinations_with_replacement(possible, size):
                inst = {"num_vars": m, "clauses": [list(c) for c in combo]}
                tests_run += 1
                expected = solve_one_in_three_sat(inst)
                out = reduce(inst)
                SubsetSum.validate(out)
                got = solve_subset_sum(out)
                assert got == expected, (inst, out, expected, got)
                tests_passed += 1
                exhaustive += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed} exhaustive={exhaustive}")
    assert tests_run == tests_passed
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

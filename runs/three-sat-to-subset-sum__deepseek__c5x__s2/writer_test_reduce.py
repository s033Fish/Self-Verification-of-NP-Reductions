"""Tests for the 3-SAT -> Subset Sum reduction in reduce.py.

Includes independent brute-force solvers for both problems (written from the
definitions in problems.py) and randomized/exhaustive comparisons.
"""

from __future__ import annotations

import itertools
import random
import sys

from reduce import reduce
from problems import ThreeSat, SubsetSum


# ----------------------------------------------------------------------
# Brute-force solvers

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[v-1] is the truth value of variable v
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to target (meet-in-the-middle for speed)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    if not numbers:
        return False

    def subset_sums(values):
        sums = {0}
        for value in values:
            sums |= {s + value for s in sums}
        return sums

    mid = len(numbers) // 2
    left = subset_sums(numbers[:mid])
    right = subset_sums(numbers[mid:])
    return any((target - s) in right for s in left)


# ----------------------------------------------------------------------
# Instance generators (small, valid instances)

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 6) -> dict:
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if num_vars < 3:
            # A clause requires 3 distinct variables; skip if impossible.
            num_clauses = 0
            break
        variables = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def exhaustive_three_sat_instances(max_vars: int = 3):
    """All 3-SAT instances over up to max_vars variables with <= 2 clauses."""
    for num_vars in range(0, max_vars + 1):
        if num_vars < 3:
            yield {"num_vars": num_vars, "clauses": []}
            continue
        literal_choices = []
        for variables in itertools.combinations(range(1, num_vars + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                literal_choices.append([s * v for s, v in zip(signs, variables)])
        # Empty formula.
        yield {"num_vars": num_vars, "clauses": []}
        # One clause.
        for clause in literal_choices:
            yield {"num_vars": num_vars, "clauses": [clause]}
        # Two clauses.
        for c1 in literal_choices:
            for c2 in literal_choices:
                yield {"num_vars": num_vars, "clauses": [c1, c2]}


# ----------------------------------------------------------------------
# Tests

def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(condition: bool, message: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            print("FAIL:", message)

    # 1. Edge cases of the reduction output.
    check(reduce({"num_vars": 0, "clauses": []}) == {"numbers": [], "target": 0},
          "empty formula reduces to empty instance with target 0")

    # 2. Every reduced instance must be a valid Subset Sum instance.
    rng = random.Random(12345)
    for _ in range(200):
        inst = random_three_sat(rng)
        ThreeSat.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)

    # 3. Exhaustive small instances: answers must match.
    for inst in exhaustive_three_sat_instances(max_vars=3):
        ThreeSat.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        expected = solve_three_sat(inst)
        got = solve_subset_sum(out)
        check(got == expected,
              f"mismatch for {inst}: sat={expected}, subset_sum={got}, out={out}")

    # 4. Random instances: answers must match.
    for _ in range(400):
        inst = random_three_sat(rng, max_vars=6, max_clauses=8)
        ThreeSat.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        expected = solve_three_sat(inst)
        got = solve_subset_sum(out)
        check(got == expected,
              f"mismatch for {inst}: sat={expected}, subset_sum={got}")

    # 5. A few hand-crafted cases.
    hand_crafted = [
        ({"num_vars": 3, "clauses": [[1, 2, 3]]}, True),
        ({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, True),
        ({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]}, True),
        # All 8 clauses over 3 vars: unsatisfiable.
        ({"num_vars": 3, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]}, False),
        # Repeated clause.
        ({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, True),
        # Unused variable.
        ({"num_vars": 5, "clauses": [[1, 2, 3]]}, True),
    ]
    for inst, expected in hand_crafted:
        ThreeSat.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        got = solve_subset_sum(out)
        check(got == expected,
              f"hand-crafted mismatch for {inst}: expected={expected}, got={got}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_passed == tests_run else 1


if __name__ == "__main__":
    sys.exit(main())

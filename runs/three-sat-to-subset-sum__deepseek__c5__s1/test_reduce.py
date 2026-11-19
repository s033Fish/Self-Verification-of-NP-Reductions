"""Independent tests for reduce.py: 3-SAT -> Subset Sum.

We write our own brute-force solvers from the problem definitions, then
compare solver answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the definitions.

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
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


def _subset_sums(nums):
    sums = {0}
    for a in nums:
        sums |= {s + a for s in sums}
    return sums


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target (meet in the middle)."""
    numbers = list(instance["numbers"])
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    half = len(numbers) // 2
    left = _subset_sums(numbers[:half])
    right = _subset_sums(numbers[half:])
    return any((target - s) in right for s in left)


# ----------------------------------------------------------------------
# Instance generation.

def random_three_sat(rng: random.Random, num_vars: int, num_clauses: int) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_three_sat(num_vars: int, num_clauses: int):
    """Exhaustively enumerate all formulas with given shape (small only)."""
    var_triples = list(itertools.combinations(range(1, num_vars + 1), 3))
    signed = []
    for triple in var_triples:
        for signs in itertools.product([1, -1], repeat=3):
            signed.append([s * v for s, v in zip(signs, triple)])
    for combo in itertools.product(signed, repeat=num_clauses):
        yield {"num_vars": num_vars, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Tests.

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_subset_sum(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, expected, got))

    # Edge case: no clauses, various m (including m=0).
    for m in range(0, 8):
        check({"num_vars": m, "clauses": []}, f"no-clauses m={m}")

    # Exhaustive small cases.
    for num_vars, num_clauses in [(3, 1), (3, 2), (3, 3), (4, 1), (4, 2), (4, 3)]:
        for inst in all_three_sat(num_vars, num_clauses):
            check(inst, f"exhaustive n={num_vars} k={num_clauses}")

    # Random cases, including duplicate clauses and unused variables.
    rng = random.Random(12345)
    for _ in range(5000):
        n = rng.randint(3, 9)
        k = rng.randint(0, 9)
        inst = random_three_sat(rng, n, k)
        if inst["clauses"] and rng.random() < 0.3:
            inst["clauses"].append(list(rng.choice(inst["clauses"])))
        check(inst, "random")

    # Targeted cases: unsatisfiable and satisfiable structures.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "targeted")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                       [1, -2, 3], [-1, 2, -3]]}, "targeted")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "dup")
    check({"num_vars": 5, "clauses": [[1, 2, 3]]}, "unused vars")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for label, inst, red, exp, got in failures[:10]:
            print(f"  {label}: expected={exp} got={got}")
            print(f"    instance={inst}")
            print(f"    reduced={red}")
    else:
        print("ALL PASSED")

    # Solver self-consistency on edge cases.
    assert solve_subset_sum({"numbers": [], "target": 0}) is True
    assert solve_subset_sum({"numbers": [], "target": 5}) is False
    assert solve_subset_sum({"numbers": [1, 2], "target": -1}) is False
    assert solve_three_sat({"num_vars": 0, "clauses": []}) is True

    return tests_run, tests_passed


if __name__ == "__main__":
    main()

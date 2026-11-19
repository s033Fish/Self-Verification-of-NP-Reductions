"""Tests for the 1-in-3-SAT -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three_sat(instance) -> bool:
    """Brute force over all assignments of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            count = sum(1 for var in clause if bits[var - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """DP over reachable sums; handles t < 0 and empty list."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in numbers:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators for small random tests.

def random_one_in_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    if num_vars >= 3:
        for _ in range(num_clauses):
            clause = rng.sample(range(1, num_vars + 1), 3)
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(name, condition):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            failures.append(name)

    # --- explicit edge cases ---
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [3, 4, 5], [5, 6, 1]]},
    ]
    for inst in edge_cases:
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        got = solve_subset_sum(out)
        check(f"edge {inst}", expected == got)

    # --- exhaustive small formulas ---
    # All formulas with m in 0..4 and up to 2 clauses over the 3-subsets.
    for m in range(0, 5):
        triples = list(itertools.combinations(range(1, m + 1), 3))
        clause_choices = [None] + triples  # None means no clause
        # formulas with 0, 1 or 2 clauses
        formula_lists = [[]]
        formula_lists += [[c] for c in triples]
        formula_lists += [[c1, c2] for c1 in triples for c2 in triples]
        for clauses in formula_lists:
            inst = {"num_vars": m, "clauses": [list(c) for c in clauses]}
            OneInThreeSat.validate(inst)
            expected = solve_one_in_three_sat(inst)
            out = reduce(inst)
            SubsetSum.validate(out)
            got = solve_subset_sum(out)
            check(f"exhaustive {inst}", expected == got)

    # --- random tests ---
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_one_in_three_sat(rng, max_vars=6, max_clauses=6)
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        got = solve_subset_sum(out)
        check(f"random {inst}", expected == got)

    # --- check reduction output shape is sane ---
    inst = {"num_vars": 3, "clauses": [[1, 2, 3]]}
    out = reduce(inst)
    check("output keys", set(out) == {"numbers", "target"})
    check("two numbers per var", len(out["numbers"]) == 2 * inst["num_vars"])

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

"""Brute-force solvers + randomized/exhaustive tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import SubsetSum, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the definitions in problems.py
# ----------------------------------------------------------------------

def solve_subset_sum(instance: dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # Exact DP over achievable sums (handles huge ints fine for small tests).
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def solve_sat(instance: dict) -> bool:
    """Complete DPLL search (exhaustive, with unit propagation)."""
    clauses = [list(c) for c in instance["clauses"]]
    num_vars = instance["num_vars"]

    def dpll(assignment: dict[int, bool]) -> bool:
        clauses_local = clauses
        while True:
            # unit propagation
            unit = None
            for clause in clauses_local:
                unassigned = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    val = assignment.get(v)
                    if val is None:
                        unassigned.append(lit)
                    elif (lit > 0) == val:
                        satisfied = True
                        break
                if satisfied:
                    continue
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            assignment[abs(unit)] = unit > 0

        # pick an unassigned variable that appears
        var = None
        for clause in clauses_local:
            for lit in clause:
                v = abs(lit)
                if v not in assignment:
                    var = v
                    break
            if var is not None:
                break
        if var is None:
            return True  # all clauses satisfied

        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(new_assignment):
                return True
        return False

    return dpll({})


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check(instance: dict) -> None:
    """Validate, reduce, validate output, and compare answers."""
    SubsetSum.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_subset_sum(instance)
    got = solve_sat(reduced)
    assert got == expected, (
        f"mismatch for {instance}: expected {expected}, reduction gave {got}\n"
        f"reduced={reduced}"
    )


def main() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # --- explicit edge cases -------------------------------------------
    run({"numbers": [], "target": 0})
    run({"numbers": [], "target": 5})
    run({"numbers": [], "target": -3})
    run({"numbers": [1, 2, 3], "target": 0})
    run({"numbers": [1, 2, 3], "target": -1})
    run({"numbers": [1, 2, 3], "target": 6})
    run({"numbers": [1, 2, 3], "target": 7})
    run({"numbers": [5, 5, 5], "target": 10})
    run({"numbers": [5, 5, 5], "target": 15})
    run({"numbers": [0, 0, 0], "target": 0})
    run({"numbers": [0, 0, 0], "target": 1})
    run({"numbers": [0, 4], "target": 4})
    run({"numbers": [10 ** 18, 1], "target": 10 ** 18})
    run({"numbers": [10 ** 18, 1], "target": 10 ** 18 + 1})
    run({"numbers": [10 ** 18, 1], "target": 10 ** 18 - 1})

    # --- exhaustive small instances ------------------------------------
    for n in range(0, 4):
        for numbers in itertools.product(range(0, 4), repeat=n):
            for target in range(-1, 10):
                run({"numbers": list(numbers), "target": target})

    # --- randomized instances ------------------------------------------
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 7)
        numbers = [rng.randint(0, 30) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 5)
        run({"numbers": numbers, "target": target})

    # --- randomized with big values ------------------------------------
    for _ in range(100):
        n = rng.randint(0, 5)
        numbers = [rng.randint(0, 10 ** 9) for _ in range(n)]
        target = rng.randint(-1, sum(numbers) + 10 ** 9)
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

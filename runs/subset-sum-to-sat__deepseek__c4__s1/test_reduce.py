"""Brute-force solvers and randomized tests for reduce.py."""

import itertools
import json
import random

from problems import Sat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def solve_sat(instance):
    """DPLL with unit propagation; complete and exact."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assignment):
        new = []
        for clause in clauses:
            satisfied = False
            rest = []
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0) == assignment[var]:
                        satisfied = True
                        break
                else:
                    rest.append(lit)
            if satisfied:
                continue
            if not rest:
                return None  # empty clause -> conflict
            new.append(rest)
        return new

    def unit_propagate(clauses, assignment):
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                return clauses, assignment
            var = abs(unit)
            value = unit > 0
            if var in assignment:
                if assignment[var] != value:
                    return None, None
                clauses = [c for c in clauses if c != [unit]]
                continue
            assignment = dict(assignment)
            assignment[var] = value
            clauses = simplify(clauses, {var: value})
            if clauses is None:
                return None, None

    def dpll(clauses, assignment):
        if any(len(c) == 0 for c in clauses):
            return None
        result = unit_propagate(clauses, assignment)
        if result == (None, None):
            return None
        clauses, assignment = result
        if not clauses:
            return assignment
        # pick a variable
        var = abs(clauses[0][0])
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            new_clauses = simplify(clauses, {var: value})
            if new_clauses is None:
                continue
            res = dpll(new_clauses, new_assignment)
            if res is not None:
                return res
        return None

    return dpll(clauses, {}) is not None


# ----------------------------------------------------------------------
# Tests.

def check(instance):
    SubsetSum.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = solve_subset_sum(instance)
    got = solve_sat(out)
    assert expected == got, (instance, out, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    hand = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -5},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [5], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [1, 2, 3], "target": 0},
        {"numbers": [2, 4, 6], "target": 5},
        {"numbers": [3, 3, 3], "target": 6},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18 + 1},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18 - 1},
        {"numbers": [7, 0, 0, 7], "target": 14},
        {"numbers": [7, 0, 0, 7], "target": 8},
    ]
    for inst in hand:
        run(inst)

    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    for _ in range(150):
        n = rng.randint(0, 10)
        numbers = [rng.randint(0, 10 ** rng.randint(1, 9)) for _ in range(n)]
        target = rng.choice([
            rng.randint(0, sum(numbers)),
            rng.randint(-2, sum(numbers) + 2),
        ])
        run({"numbers": numbers, "target": target})

    for _ in range(100):
        n = rng.randint(0, 9)
        numbers = [rng.choice([0, 0, 1, 2, 5]) for _ in range(n)]
        target = rng.randint(-1, sum(numbers) + 1)
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()

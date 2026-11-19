"""Tests for the Subset Sum -> SAT reduction.

Contains brute-force solvers for both problems (problems.py has none) and
compares their answers on many small instances, including edge cases.
A small DPLL solver handles the large-number cases whose reduced formulas
have too many variables for exhaustive enumeration.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_subset_sum(instance: dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def solve_sat_bruteforce(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False  # empty clause can never be satisfied
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = {v: bits[v - 1] for v in range(1, num_vars + 1)}
        if all(
            any(
                (lit > 0 and assignment[lit]) or (lit < 0 and not assignment[-lit])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def _assign(clauses, lit):
    """Apply literal lit as true; return simplified clauses or None if unsat."""
    new = []
    for clause in clauses:
        if lit in clause:
            continue
        reduced = [x for x in clause if x != -lit]
        if not reduced:
            return None
        new.append(reduced)
    return new


def solve_sat_dpll(instance: dict) -> bool:
    clauses = [list(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False

    def dpll(clauses):
        clauses = [list(c) for c in clauses]
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 0:
                    return False
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            clauses = _assign(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        var = abs(clauses[0][0])
        for lit in (var, -var):
            result = _assign(clauses, lit)
            if result is not None and dpll(result):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance: dict) -> bool:
    if instance["num_vars"] <= 16:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Test harness.

tests_run = 0
tests_passed = 0
failures = []


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(message)


def compare(instance: dict, label: str) -> None:
    SOURCE.validate(instance)
    expected = solve_subset_sum(instance)
    result = reduce(instance)
    TARGET.validate(result)
    actual = solve_sat(result)
    check(
        expected == actual,
        f"{label}: instance={instance!r} expected={expected} got={actual}",
    )


# ----------------------------------------------------------------------
# Hand-picked edge cases.

edge_cases = [
    {"numbers": [], "target": 0},
    {"numbers": [], "target": 1},
    {"numbers": [], "target": -1},
    {"numbers": [5], "target": 0},
    {"numbers": [5], "target": 5},
    {"numbers": [5], "target": 4},
    {"numbers": [5], "target": 6},
    {"numbers": [5], "target": -3},
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [0, 0, 0], "target": 1},
    {"numbers": [0, 7], "target": 7},
    {"numbers": [0, 7], "target": 8},
    {"numbers": [1, 2, 3], "target": 6},
    {"numbers": [1, 2, 3], "target": 7},
    {"numbers": [1, 2, 3], "target": 3},
    {"numbers": [2, 2, 2], "target": 4},
    {"numbers": [2, 2, 2], "target": 5},
    {"numbers": [1, 1, 1, 1], "target": 2},
    {"numbers": [10, 20, 30], "target": 30},
    {"numbers": [10, 20, 30], "target": 40},
    {"numbers": [10, 20, 30], "target": 60},
    {"numbers": [10, 20, 30], "target": 61},
    {"numbers": [1000000000000000000, 1], "target": 1000000000000000000},
    {"numbers": [1000000000000000000, 1], "target": 1000000000000000001},
    {"numbers": [1000000000000000000, 1], "target": 999999999999999999},
    {"numbers": [3, 3, 3, 3], "target": 9},
    {"numbers": [3, 3, 3, 3], "target": 10},
    {"numbers": [2 ** 40, 2 ** 40, 2 ** 40], "target": 2 ** 41},
    {"numbers": [2 ** 40, 2 ** 40, 2 ** 40], "target": 2 ** 41 + 1},
    {"numbers": [123456789, 987654321, 555555555], "target": 1111111110},
    {"numbers": [123456789, 987654321, 555555555], "target": 1111111111},
]

for i, inst in enumerate(edge_cases):
    compare(inst, f"edge#{i}")


# ----------------------------------------------------------------------
# Randomized small instances.

rng = random.Random(12345)
for trial in range(400):
    n = rng.randint(0, 8)
    max_val = rng.choice([1, 2, 3, 5, 10])
    numbers = [rng.randint(0, max_val) for _ in range(n)]
    total = sum(numbers)
    target = rng.randint(-2, total + 2)
    compare({"numbers": numbers, "target": target}, f"random#{trial}")

# Random instances biased toward feasible targets.
for trial in range(200):
    n = rng.randint(1, 7)
    numbers = [rng.randint(0, 6) for _ in range(n)]
    subset = [a for a in numbers if rng.random() < 0.5]
    target = sum(subset)
    compare({"numbers": numbers, "target": target}, f"feasible#{trial}")

# Medium instances with larger values (DPLL path).
for trial in range(50):
    n = rng.randint(1, 10)
    numbers = [rng.randint(0, 1000) for _ in range(n)]
    total = sum(numbers)
    if rng.random() < 0.5:
        target = sum(a for a in numbers if rng.random() < 0.5)
    else:
        target = rng.randint(0, total)
    compare({"numbers": numbers, "target": target}, f"medium#{trial}")


# ----------------------------------------------------------------------
# Cross-check the two SAT solvers on small random formulas.
for trial in range(200):
    num_vars = rng.randint(0, 6)
    clauses = []
    for _ in range(rng.randint(0, 8)):
        clause = []
        for _ in range(rng.randint(0, 4)):
            v = rng.randint(1, num_vars) if num_vars else 1
            if num_vars == 0:
                break
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    formula = {"num_vars": num_vars, "clauses": clauses}
    check(
        solve_sat_bruteforce(formula) == solve_sat_dpll(formula),
        f"solver-mismatch#{trial}: {formula!r}",
    )


# ----------------------------------------------------------------------
# Exhaustive sweep over all small instances.

for n in range(0, 5):
    for numbers in itertools.product(range(0, 4), repeat=n):
        total = sum(numbers)
        for target in range(-1, total + 2):
            compare(
                {"numbers": list(numbers), "target": target},
                f"exhaustive n={n} {numbers} t={target}",
            )


# ----------------------------------------------------------------------
# Report.

print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print("FAILURES:")
    for failure in failures[:10]:
        print("  " + failure)
    raise SystemExit(1)
print("ALL TESTS PASSED")

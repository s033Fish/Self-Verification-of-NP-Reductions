"""Tests for the Subset Sum -> SAT reduction."""

import itertools
import random

from problems import SubsetSum, Sat
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def solve_sat(instance):
    """Complete DPLL solver (unit propagation + branching)."""
    clauses = []
    for c in instance["clauses"]:
        s = set(c)
        if any(-lit in s for lit in s):
            continue  # tautology, always satisfied
        clauses.append(s)

    def rec(clauses):
        clauses = [set(c) for c in clauses]
        while True:
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    unit = next(iter(c))
                    break
            if unit is None:
                break
            new = []
            for c in clauses:
                if unit in c:
                    continue
                if -unit in c:
                    c2 = c - {-unit}
                    if len(c2) == 0:
                        return False
                    new.append(c2)
                else:
                    new.append(c)
            clauses = new
        if not clauses:
            return True
        lit = next(iter(clauses[0]))
        for val in (True, False):
            l2 = lit if val else -lit
            new = []
            ok = True
            for c in clauses:
                if l2 in c:
                    continue
                if -l2 in c:
                    c2 = c - {-l2}
                    if len(c2) == 0:
                        ok = False
                        break
                    new.append(c2)
                else:
                    new.append(c)
            if ok and rec(new):
                return True
        return False

    return rec(clauses)


# ---------------------------------------------------------------- helpers

def check(instance):
    SubsetSum.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    a = solve_subset_sum(instance)
    b = solve_sat(out)
    assert a == b, (instance, out, a, b)
    return a


def main():
    random.seed(12345)
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # ---- explicit edge cases ----
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [5], "target": -3},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 6},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0], "target": 1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [2, 4, 6], "target": 3},
        {"numbers": [1000000000000, 1], "target": 1000000000001},
        {"numbers": [1000000000000, 1], "target": 1000000000000},
        {"numbers": [1000000000000, 1], "target": 2},
        {"numbers": [7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7], "target": 14},
        {"numbers": [7, 7, 7], "target": 15},
    ]
    for inst in edge_cases:
        run(inst)

    # ---- exhaustive small instances ----
    for n in range(0, 5):
        for numbers in itertools.product(range(0, 4), repeat=n):
            for target in range(-2, sum(numbers) + 3):
                run({"numbers": list(numbers), "target": target})

    # ---- random instances ----
    for _ in range(400):
        n = random.randint(0, 8)
        numbers = [random.randint(0, 30) for _ in range(n)]
        target = random.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    for _ in range(60):
        n = random.randint(0, 6)
        numbers = [random.randint(0, 10**12) for _ in range(n)]
        target = random.choice([
            random.randint(-5, 5),
            random.randint(0, sum(numbers)),
            sum(numbers),
            sum(numbers) + 1,
        ])
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

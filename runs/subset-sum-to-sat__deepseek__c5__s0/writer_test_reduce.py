"""Tests for the Subset Sum -> SAT reduction."""

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.
# Subset Sum: brute force over all sub-lists.
# SAT: exact DPLL (brute force enumeration is infeasible for the larger
# reductions produced by the adder circuit).

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    t = instance["target"]
    if t < 0:
        return False
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == t:
                return True
    return False


def _lit_true(lit, assign):
    v = abs(lit)
    if v not in assign:
        return None
    return assign[v] if lit > 0 else not assign[v]


def _dpll(clauses, assign):
    # unit propagation
    while True:
        unit = None
        for clause in clauses:
            unassigned = []
            satisfied = False
            for lit in clause:
                val = _lit_true(lit, assign)
                if val is True:
                    satisfied = True
                    break
                if val is None:
                    unassigned.append(lit)
            if satisfied:
                continue
            if not unassigned:
                return False
            if len(unassigned) == 1:
                unit = unassigned[0]
                break
        if unit is None:
            break
        assign[abs(unit)] = unit > 0

    # all clauses satisfied?
    all_sat = True
    for clause in clauses:
        if not any(_lit_true(lit, assign) is True for lit in clause):
            all_sat = False
            break
    if all_sat:
        return True

    # choose an unassigned variable
    var = None
    for clause in clauses:
        for lit in clause:
            if abs(lit) not in assign:
                var = abs(lit)
                break
        if var is not None:
            break
    if var is None:
        return True

    for value in (True, False):
        new_assign = dict(assign)
        new_assign[var] = value
        if _dpll(clauses, new_assign):
            return True
    return False


def solve_sat(instance):
    clauses = [list(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False
    return _dpll(clauses, {})


# ----------------------------------------------------------------------

def check(instance):
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_subset_sum(instance)
    got = solve_sat(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Hand-picked edge cases.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [], "target": -3},
        {"numbers": [1, 2, 3], "target": 0},
        {"numbers": [1, 2, 3], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [0, 4], "target": 4},
        {"numbers": [2, 2, 2, 2], "target": 6},
        {"numbers": [2, 2, 2, 2], "target": 7},
        {"numbers": [10 ** 9, 1], "target": 10 ** 9 + 1},
        {"numbers": [10 ** 9, 1], "target": 10 ** 9},
        {"numbers": [10 ** 9, 1], "target": 10 ** 9 + 2},
        {"numbers": [3, 3, 3], "target": 9},
        {"numbers": [3, 3, 3], "target": 8},
        {"numbers": [1, 1, 1, 1, 1, 1], "target": 3},
    ]
    for inst in edge:
        run(inst)

    rng = random.Random(12345)
    # Small random tests.
    for _ in range(400):
        n = rng.randint(0, 6)
        numbers = [rng.randint(0, 8) for _ in range(n)]
        target = rng.randint(-2, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    # Larger values, fewer numbers.
    for _ in range(150):
        n = rng.randint(0, 5)
        numbers = [rng.randint(0, 40) for _ in range(n)]
        target = rng.randint(-1, sum(numbers) + 2)
        run({"numbers": numbers, "target": target})

    # Big integers to exercise bit lengths.
    for _ in range(60):
        n = rng.randint(1, 4)
        numbers = [rng.randint(0, 10 ** 6) for _ in range(n)]
        target = rng.choice([
            sum(numbers),
            sum(numbers) // 2,
            rng.randint(0, sum(numbers)),
            sum(numbers) + 1,
        ])
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

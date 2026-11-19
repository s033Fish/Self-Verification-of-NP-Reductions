"""Brute-force solvers and tests comparing them with the reduction."""

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.
# Subset Sum: exact DP over reachable sums.
# SAT: DPLL with unit propagation (exact, handles auxiliary variables).

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def solve_sat(instance):
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        clauses = [c for c in clauses]
        while True:
            # unit propagation
            unit = None
            for clause in clauses:
                if any(abs(lit) in assignment and
                       ((lit > 0) == assignment[abs(lit)]) for lit in clause):
                    continue  # satisfied
                unassigned = [lit for lit in clause if abs(lit) not in assignment]
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            assignment[abs(unit)] = unit > 0
        # all clauses satisfied?
        if all(any(abs(lit) in assignment and ((lit > 0) == assignment[abs(lit)])
                   for lit in clause) for clause in clauses):
            return True
        # pick an unassigned variable
        var = None
        for clause in clauses:
            for lit in clause:
                if abs(lit) not in assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return True
        for value in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = value
            if dpll(clauses, new_assign):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Tests

def check(instance):
    reduced = reduce(instance)
    assert set(reduced.keys()) == {"num_vars", "clauses"}
    assert isinstance(reduced["num_vars"], int) and reduced["num_vars"] >= 0
    for clause in reduced["clauses"]:
        assert isinstance(clause, list)
        for lit in clause:
            assert isinstance(lit, int) and lit != 0
            assert abs(lit) <= reduced["num_vars"]
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

    # explicit edge cases
    run({"numbers": [], "target": 0})
    run({"numbers": [], "target": 5})
    run({"numbers": [], "target": -3})
    run({"numbers": [1, 2, 3], "target": 0})
    run({"numbers": [1, 2, 3], "target": -1})
    run({"numbers": [1, 2, 3], "target": 6})
    run({"numbers": [1, 2, 3], "target": 7})
    run({"numbers": [0, 0, 0], "target": 0})
    run({"numbers": [0, 0, 0], "target": 1})
    run({"numbers": [5], "target": 5})
    run({"numbers": [5], "target": 4})
    run({"numbers": [1000000000000000000, 1], "target": 1000000000000000001})
    run({"numbers": [1000000000000000000, 1], "target": 2})
    run({"numbers": [2, 2, 2, 2], "target": 4})
    run({"numbers": [2, 2, 2, 2], "target": 3})
    run({"numbers": [7, 7, 7], "target": 14})
    run({"numbers": [7, 7, 7], "target": 21})

    # exhaustive small instances
    for n in range(0, 6):
        for numbers in itertools.product(range(0, 5), repeat=n):
            total = sum(numbers)
            for target in range(-1, total + 2):
                run({"numbers": list(numbers), "target": target})

    # random instances
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        numbers = [rng.randint(0, 40) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    # random instances with big values
    for _ in range(300):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 10 ** 15) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

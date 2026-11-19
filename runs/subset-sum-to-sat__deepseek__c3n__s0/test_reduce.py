"""Brute-force solvers and tests comparing Subset Sum with its SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import Sat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_subset_sum(instance) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def solve_sat(instance) -> bool:
    """DPLL with unit propagation (exact, exponential worst case)."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assignment):
        # returns (new_clauses, ok) with assignment applied
        out = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for l in clause:
                v = abs(l)
                if v in assignment:
                    if assignment[v] == (l > 0):
                        satisfied = True
                        break
                else:
                    new_clause.append(l)
            if satisfied:
                continue
            out.append(new_clause)
        return out

    def dpll(clauses, assignment):
        while True:
            # unit propagation
            unit = None
            for clause in clauses:
                if len(clause) == 0:
                    return False
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            assignment = dict(assignment)
            assignment[abs(unit)] = unit > 0
            clauses = simplify(clauses, {abs(unit): unit > 0})
        if not clauses:
            return True
        # choose a variable
        var = abs(clauses[0][0])
        for value in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = value
            if dpll(simplify(clauses, {var: value}), new_assign):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check(instance, label=""):
    SubsetSum.validate(instance)
    expected = solve_subset_sum(instance)
    out = reduce(instance)
    Sat.validate(out)
    got = solve_sat(out)
    assert got == expected, (
        f"mismatch {label}: instance={instance} expected={expected} got={got} "
        f"reduction={out}"
    )
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance, label=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance, label)
        tests_passed += 1

    # ---- explicit edge cases ------------------------------------------
    run({"numbers": [], "target": 0}, "empty t=0")
    run({"numbers": [], "target": 1}, "empty t=1")
    run({"numbers": [], "target": -1}, "empty t=-1")
    run({"numbers": [5], "target": 0}, "t=0")
    run({"numbers": [5], "target": -3}, "t<0")
    run({"numbers": [5], "target": 5}, "single yes")
    run({"numbers": [5], "target": 4}, "single no")
    run({"numbers": [0, 0, 0], "target": 0}, "zeros t=0")
    run({"numbers": [0, 0, 0], "target": 1}, "zeros t=1")
    run({"numbers": [1, 1, 1], "target": 2}, "repeats yes")
    run({"numbers": [1, 1, 1], "target": 4}, "repeats no")
    run({"numbers": [1000000000000000000000], "target": 1000000000000000000000},
        "big number yes")
    run({"numbers": [1000000000000000000000], "target": 999999999999999999999},
        "big number no")

    # ---- exhaustive small cases ---------------------------------------
    for n in range(0, 6):
        for numbers in itertools.product(range(4), repeat=n):
            total = sum(numbers)
            for target in range(-2, total + 3):
                run({"numbers": list(numbers), "target": target},
                    f"exhaustive n={n}")

    # ---- random cases --------------------------------------------------
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 10)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target}, "random")

    # ---- polynomial size sanity check ---------------------------------
    for n in (5, 10, 20, 40):
        numbers = [rng.randint(0, 10 ** 9) for _ in range(n)]
        out = reduce({"numbers": numbers, "target": sum(numbers) // 2})
        assert out["num_vars"] <= 100 * n * 32 + 100, (n, out["num_vars"])
        assert len(out["clauses"]) <= 100 * n * 32 + 100, (n, len(out["clauses"]))
        tests_run += 1
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()

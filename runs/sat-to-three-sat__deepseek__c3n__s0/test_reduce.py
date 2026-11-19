"""Brute-force/DPLL solvers and randomized/edge-case tests for reduce.py."""

import itertools
import random

from problems import Sat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the problem definitions).

def brute_force_solve(instance):
    """Exhaustive search; only for tiny instances."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def dpll_solve(instance):
    """DPLL with unit propagation; handles the auxiliary variables."""
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assignment):
        new = []
        for clause in clauses:
            satisfied = False
            rest = []
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if assignment[var] == (lit > 0):
                        satisfied = True
                        break
                else:
                    rest.append(lit)
            if satisfied:
                continue
            if not rest:
                return None  # conflict
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
                clauses = [c for c in clauses if unit not in c]
                continue
            assignment = dict(assignment)
            assignment[var] = value
            clauses = simplify(clauses, assignment)
            if clauses is None:
                return None, None

    def choose_var(clauses):
        for clause in clauses:
            for lit in clause:
                return abs(lit)
        return None

    def dpll(clauses, assignment):
        result = unit_propagate(clauses, assignment)
        clauses, assignment = result
        if clauses is None:
            return False
        if not clauses:
            return True
        var = choose_var(clauses)
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            new_clauses = simplify(clauses, new_assignment)
            if new_clauses is None:
                continue
            if dpll(new_clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation.

def random_sat_instance(rng, max_vars=5, max_clauses=6, max_len=5):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def check(instance, solver):
    Sat.validate(instance)
    reduced = reduce(instance)
    ThreeSat.validate(reduced)
    expected = solver(instance)
    got = solver(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance, label, solver=dpll_solve):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance, solver)
            tests_passed += 1
        except AssertionError as exc:
            print("FAIL", label, exc)

    # Hand-crafted edge cases.
    run({"num_vars": 0, "clauses": []}, "empty formula m=0")
    run({"num_vars": 0, "clauses": [[]]}, "empty clause m=0")
    run({"num_vars": 3, "clauses": []}, "no clauses")
    run({"num_vars": 3, "clauses": [[]]}, "empty clause")
    run({"num_vars": 1, "clauses": [[1]]}, "unit positive")
    run({"num_vars": 1, "clauses": [[-1]]}, "unit negative")
    run({"num_vars": 1, "clauses": [[1], [-1]]}, "contradiction")
    run({"num_vars": 2, "clauses": [[1, 2]]}, "two literals")
    run({"num_vars": 2, "clauses": [[1, -1]]}, "tautology")
    run({"num_vars": 2, "clauses": [[1, 1, 1]]}, "repeats")
    run({"num_vars": 3, "clauses": [[1, 2, 3]]}, "three literals")
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4]]}, "four literals")
    run({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]}, "six literals")
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]}, "two long")
    run({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]}, "long unsat")
    run({"num_vars": 3, "clauses": [[1], [2], [3]]}, "three units")
    run({"num_vars": 3, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]}, "unsat 2cnf")
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4]] * 3}, "duplicate clauses")
    run({"num_vars": 2, "clauses": [[1, -1, 2]]}, "tautology mixed")
    run({"num_vars": 3, "clauses": [[1, 1, -2, -2, 3]]}, "dupes then 3")
    run({"num_vars": 7, "clauses": [[1, 2, 3, 4, 5, 6, 7]]}, "seven literals")
    run({"num_vars": 8, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8]]}, "eight literals")

    # Cross-check the two solvers on tiny instances.
    rng0 = random.Random(7)
    for i in range(300):
        instance = random_sat_instance(rng0, max_vars=4, max_clauses=4, max_len=4)
        run(instance, f"cross {i}", solver=brute_force_solve)
        run(instance, f"cross-dpll {i}", solver=dpll_solve)

    # Randomized tests, small.
    rng = random.Random(12345)
    for i in range(3000):
        instance = random_sat_instance(rng)
        run(instance, f"random {i}")

    # Larger random instances with more variables/clauses.
    rng2 = random.Random(999)
    for i in range(1000):
        instance = random_sat_instance(rng2, max_vars=8, max_clauses=12, max_len=8)
        run(instance, f"random-large {i}")

    # Structured instances: many long clauses, mixed with units.
    rng3 = random.Random(4242)
    for i in range(500):
        m = rng3.randint(1, 6)
        clauses = []
        for _ in range(rng3.randint(1, 6)):
            length = rng3.randint(1, 9)
            clauses.append([rng3.choice([1, -1]) * rng3.randint(1, m) for _ in range(length)])
        run({"num_vars": m, "clauses": clauses}, f"structured {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

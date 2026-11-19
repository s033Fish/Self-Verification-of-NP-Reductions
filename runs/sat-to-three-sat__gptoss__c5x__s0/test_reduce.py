"""Independent verification tests for reduce.py (SAT -> 3-SAT).

We implement our own brute-force solvers directly from the problem
definitions in problems.py (which provides no solvers), then compare the
answer of every small source instance with the answer of its reduction.

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import Sat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def cnf_solve(instance):
    """Brute force CNF satisfiability for either Sat or ThreeSat format.

    Variables are 1..m.  A clause is satisfied if any literal is true.
    Empty clause is unsatisfiable; empty formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        satisfied = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
                for lit in clause
            ):
                satisfied = False
                break
        if satisfied:
            return True
    return False


sat_solve = cnf_solve
three_sat_solve = cnf_solve


# ----------------------------------------------------------------------
# Instance generators (small, so brute force is feasible).
# ----------------------------------------------------------------------

def all_clauses(num_vars, max_len):
    literals = [lit for v in range(1, num_vars + 1) for lit in (v, -v)]
    clauses = []
    for length in range(0, max_len + 1):
        for combo in itertools.combinations_with_replacement(literals, length):
            clauses.append(list(combo))
    return clauses


def exhaustive_instances(max_vars=3, max_clauses=2, max_len=4):
    for num_vars in range(0, max_vars + 1):
        pool = all_clauses(num_vars, max_len)
        for r in range(0, max_clauses + 1):
            for subset in itertools.combinations(pool, r):
                yield {"num_vars": num_vars, "clauses": [list(c) for c in subset]}


def random_instances(count, seed=0):
    rng = random.Random(seed)
    for _ in range(count):
        num_vars = rng.randint(0, 6)
        literals = [lit for v in range(1, num_vars + 1) for lit in (v, -v)]
        clauses = []
        for _ in range(rng.randint(0, 7)):
            length = rng.randint(0, 8)
            if num_vars == 0:
                clauses.append([])
            else:
                clauses.append([rng.choice(literals) for _ in range(length)])
        yield {"num_vars": num_vars, "clauses": clauses}


def explicit_edge_instances():
    return [
        {"num_vars": 0, "clauses": []},                 # empty, sat
        {"num_vars": 0, "clauses": [[]]},               # empty clause, unsat
        {"num_vars": 5, "clauses": []},                 # no clauses, sat
        {"num_vars": 3, "clauses": [[]]},               # empty clause, unsat
        {"num_vars": 1, "clauses": [[1], [-1]]},        # unsat
        {"num_vars": 1, "clauses": [[1, -1]]},          # tautology, sat
        {"num_vars": 2, "clauses": [[1, 1, 1, 1]]},     # repeated literal
        {"num_vars": 4, "clauses": [[1, 2, 3, 4, 4, -2]]},  # long, tautology
        {"num_vars": 4, "clauses": [[1, 2, 3, 4, 1, 2]]},   # long, no tautology
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, # duplicate clause
        {"num_vars": 6, "clauses": [[1, -2, 3, -4, 5, -6, 1, 2]]},  # len 8
    ]


# ----------------------------------------------------------------------
# Test driver.
# ----------------------------------------------------------------------

def check(instance, failures):
    """Validate, reduce, validate target, compare answers. Return True if ok."""
    Sat.validate(instance)
    reduced = reduce(instance)
    ThreeSat.validate(reduced)
    expected = sat_solve(instance)
    got = three_sat_solve(reduced)
    if expected != got:
        failures.append((instance, reduced, expected, got))
        return False
    return True


def main():
    failures = []
    tests_run = 0
    tests_passed = 0

    sources = list(exhaustive_instances())
    sources += explicit_edge_instances()
    sources += list(random_instances(30000, seed=2024))

    for instance in sources:
        tests_run += 1
        if check(instance, failures):
            tests_passed += 1

    # Also verify a few larger long-clause instances explicitly.
    for length in range(4, 13):
        for _ in range(200):
            rng = random.Random(length * 1000 + _)
            num_vars = 3
            literals = [1, 2, 3, -1, -2, -3]
            clause = [rng.choice(literals) for _ in range(length)]
            instance = {"num_vars": num_vars, "clauses": [clause]}
            tests_run += 1
            if check(instance, failures):
                tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for instance, reduced, expected, got in failures[:10]:
            print("  src:", instance)
            print("  tgt:", reduced)
            print("  expected", expected, "got", got)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

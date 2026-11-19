"""Independent tests for reduce.py: 1-in-3-SAT (positive) -> 3-SAT.

problems.py provides only validate(); there are no solvers.  We therefore
implement our own solvers directly from the definitions:

  * solve_one_in_three_sat: brute force over all 2^m assignments, requiring
    EXACTLY ONE true variable in every clause (vacuously true with no clauses).
  * solve_three_sat_bruteforce: brute force, requiring >= 1 true literal per
    clause.
  * solve_three_sat_dpll: a DPLL solver so we can also check reductions whose
    auxiliary variables make naive brute force too slow.

We generate many small source instances (including edge cases), reduce them,
and check (a) the reduced instance is a valid ThreeSat instance and (b) the
source and target answers agree.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the definitions
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance):
    """True iff some assignment makes EXACTLY ONE var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if sum(1 for v in clause if bits[v - 1]) != 1:
                ok = False
                break
        if ok:
            return True
    return not clauses  # no clauses -> vacuously satisfiable


def solve_three_sat_bruteforce(instance):
    """True iff some assignment makes every clause have >= 1 true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat_dpll(instance):
    """DPLL satisfiability check for 3-SAT."""
    def dpll(clauses, assignment):
        simplified = []
        for clause in clauses:
            sat = False
            rest = []
            for lit in clause:
                v = abs(lit)
                val = assignment.get(v)
                if val is None:
                    rest.append(lit)
                elif (lit > 0) == val:
                    sat = True
                    break
            if sat:
                continue
            if not rest:
                return False
            simplified.append(rest)
        if not simplified:
            return True
        for clause in simplified:
            if len(clause) == 1:
                lit = clause[0]
                v = abs(lit)
                val = lit > 0
                if v in assignment and assignment[v] != val:
                    return False
                new = dict(assignment)
                new[v] = val
                return dpll(simplified, new)
        lit = simplified[0][0]
        v = abs(lit)
        for val in (True, False):
            new = dict(assignment)
            new[v] = val
            if dpll(simplified, new):
                return True
        return False

    return dpll(instance["clauses"], {})


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_positive_clauses(m):
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


def gen_small_instances():
    """Small instances brute-forceable even after adding auxiliaries."""
    instances = []

    # Edge case: no clauses, including m = 0.
    for m in range(0, 7):
        instances.append({"num_vars": m, "clauses": []})

    # All single clauses for m = 3,4,5.
    for m in range(3, 6):
        for c in all_positive_clauses(m):
            instances.append({"num_vars": m, "clauses": [c]})

    # Exhaustive over all clause multisets of size <= 3 for m = 4.
    m, pool = 4, all_positive_clauses(4)
    for k in range(0, 4):
        for combo in itertools.combinations_with_replacement(pool, k):
            instances.append({"num_vars": m, "clauses": [list(c) for c in combo]})

    # Exhaustive over all clause multisets of size <= 2 for m = 5.
    m, pool = 5, all_positive_clauses(5)
    for k in range(0, 3):
        for combo in itertools.combinations_with_replacement(pool, k):
            instances.append({"num_vars": m, "clauses": [list(c) for c in combo]})

    # Random small instances (duplicates, unused variables).
    rng = random.Random(12345)
    for _ in range(300):
        m = rng.randint(3, 4)
        pool = all_positive_clauses(m)
        k = rng.randint(0, 3)
        instances.append({"num_vars": m,
                          "clauses": [list(rng.choice(pool)) for _ in range(k)]})

    # Extra unused variables.
    for _ in range(50):
        m = rng.randint(3, 5)
        pool = all_positive_clauses(m)
        k = rng.randint(1, 2)
        instances.append({"num_vars": m,
                          "clauses": [list(rng.choice(pool)) for _ in range(k)]})

    return instances


def gen_larger_instances():
    """Larger instances checked with DPLL on the reduced formula."""
    rng = random.Random(999)
    instances = []
    for _ in range(3000):
        m = rng.randint(3, 9)
        pool = all_positive_clauses(m)
        k = rng.randint(0, 8)
        instances.append({"num_vars": m,
                          "clauses": [list(rng.choice(pool)) for _ in range(k)]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    # Small instances: brute-force both source and reduced target.
    for inst in gen_small_instances():
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        reduced = reduce(inst)

        tests_run += 1
        try:
            ThreeSat.validate(reduced)
            tests_passed += 1
        except Exception as exc:
            print("INVALID TARGET", inst, "->", reduced, exc)
            continue

        tests_run += 1
        got = solve_three_sat_bruteforce(reduced)
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected,
                  "reduced", reduced, "got", got)

    # Larger instances: brute-force source, DPLL on reduced target.
    for inst in gen_larger_instances():
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        reduced = reduce(inst)

        tests_run += 1
        try:
            ThreeSat.validate(reduced)
            tests_passed += 1
        except Exception as exc:
            print("INVALID TARGET", inst, "->", reduced, exc)
            continue

        tests_run += 1
        got = solve_three_sat_dpll(reduced)
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

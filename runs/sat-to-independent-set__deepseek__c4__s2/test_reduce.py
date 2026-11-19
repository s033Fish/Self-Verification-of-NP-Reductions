"""Brute-force solvers and tests comparing SAT answers with reduced IS answers."""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py


def sat_solve(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def is_solve(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (frozenset((u, v)) in edge_set)
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Test helpers


def check(instance: dict) -> bool:
    """Return True if reduction preserves the answer for this instance."""
    Sat.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    expected = sat_solve(instance)
    got = is_solve(reduced)
    if expected != got:
        print("MISMATCH")
        print("  source:", instance)
        print("  target:", reduced)
        print("  expected:", expected, "got:", got)
        return False
    return True


def random_instance(rng: random.Random) -> dict:
    num_vars = rng.randint(0, 4)
    num_clauses = rng.randint(0, 5)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, 3)
        clause = []
        for _ in range(length):
            v = rng.randint(1, num_vars) if num_vars > 0 else 1
            if num_vars == 0:
                # no variables available; skip literal
                continue
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance):
            tests_passed += 1

    # Hand-picked edge cases.
    run({"num_vars": 0, "clauses": []})                       # yes (no clauses)
    run({"num_vars": 0, "clauses": [[]]})                     # no (empty clause)
    run({"num_vars": 1, "clauses": [[1]]})                    # yes
    run({"num_vars": 1, "clauses": [[-1]]})                   # yes
    run({"num_vars": 1, "clauses": [[1], [-1]]})              # no
    run({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]})  # yes
    run({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]})  # no
    run({"num_vars": 3, "clauses": [[1, 1, 2], [-1, -1], [2, -3]]})  # yes
    run({"num_vars": 2, "clauses": [[1, -1]]})                # yes (tautology)
    run({"num_vars": 2, "clauses": [[1, -1], [2], [-2]]})     # no
    run({"num_vars": 3, "clauses": [[1], [1], [1]]})          # yes (dup clauses)
    run({"num_vars": 3, "clauses": [[1], [1], [-1]]})         # no

    # Exhaustive over all small formulas.
    for num_vars in range(0, 4):
        literals = [v for v in range(1, num_vars + 1)] + \
                   [-v for v in range(1, num_vars + 1)]
        # all clauses of length 0..2 (with repetition allowed)
        possible_clauses = [[]]
        possible_clauses += [[a] for a in literals]
        possible_clauses += [[a, b] for a in literals for b in literals]
        for num_clauses in range(0, 3):
            for clauses in itertools.product(possible_clauses, repeat=num_clauses):
                run({"num_vars": num_vars, "clauses": [list(c) for c in clauses]})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        run(random_instance(rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

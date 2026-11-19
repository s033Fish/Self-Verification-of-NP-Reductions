"""Brute-force solvers and tests comparing 1-in-3-SAT with its reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


def solve_one_in_three(instance):
    """Brute force 1-in-3-SAT: exactly one true variable per clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if sum(bits[v - 1] for v in clause) != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_sat(instance):
    """Brute force 3-SAT: at least one true literal per clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def random_source_instance(rng):
    m = rng.randint(0, 6)
    num_clauses = rng.randint(0, 5)
    if num_clauses > 0:
        m = max(m, 3)
    clauses = []
    for _ in range(num_clauses):
        clause = rng.sample(range(1, m + 1), 3)
        rng.shuffle(clause)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Deterministic edge cases first.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
    ]

    instances = list(edge_cases)
    for _ in range(400):
        instances.append(random_source_instance(rng))

    for inst in instances:
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three(inst)
        reduced = reduce(inst)
        ThreeSat.validate(reduced)
        got = solve_three_sat(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH:", inst, "expected", expected, "got", got, "reduced", reduced)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

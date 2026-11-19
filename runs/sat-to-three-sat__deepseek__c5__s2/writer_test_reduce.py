"""Brute-force solvers and tests for the SAT -> 3-SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import Sat, ThreeSat
from reduce import reduce


def sat_solve(instance) -> bool:
    """Brute-force SAT solver over variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
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


def three_sat_solve(instance) -> bool:
    """Brute-force 3-SAT solver (same semantics)."""
    return sat_solve(instance)


def random_sat_instance(rng: random.Random) -> dict:
    m = rng.randint(0, 5)
    n_clauses = rng.randint(0, 6)
    clauses = []
    for _ in range(n_clauses):
        length = rng.randint(0, 5)
        if m == 0:
            clause = []
        else:
            clause = [rng.choice([1, -1]) * rng.randint(1, m) for _ in range(length)]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def check(instance) -> None:
    Sat.validate(instance)
    reduced = reduce(instance)
    ThreeSat.validate(reduced)
    expected = sat_solve(instance)
    got = three_sat_solve(reduced)
    assert expected == got, (
        f"MISMATCH\nsource={instance}\nexpected={expected}\n"
        f"reduced={reduced}\ngot={got}"
    )


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Explicit edge cases.
    run({"num_vars": 0, "clauses": []})                       # yes
    run({"num_vars": 3, "clauses": []})                       # yes
    run({"num_vars": 2, "clauses": [[]]})                     # no
    run({"num_vars": 0, "clauses": [[]]})                     # no
    run({"num_vars": 1, "clauses": [[1]]})                    # yes
    run({"num_vars": 1, "clauses": [[-1]]})                   # no
    run({"num_vars": 1, "clauses": [[1, -1]]})                # yes (tautology)
    run({"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]})  # no
    run({"num_vars": 3, "clauses": [[1, 2, 3]]})              # yes
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4]]})           # yes
    run({"num_vars": 4, "clauses": [[-1, -2, -3, -4]]})       # yes
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]})  # no
    run({"num_vars": 5, "clauses": [[1, 1, 2, 2, 3, 3]]})     # yes
    run({"num_vars": 5, "clauses": [[1, 1, -1, 2]]})          # yes tautology
    run({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]})     # yes
    run({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6],
                                    [-1], [-2], [-3], [-4], [-5], [-6]]})  # no
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})   # duplicate clause yes

    # Randomised small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        run(random_sat_instance(rng))

    # Exhaustive small structured instances over m <= 2.
    for m in range(0, 3):
        lits = [l for v in range(1, m + 1) for l in (v, -v)]
        clause_pool = [[]] + [[l] for l in lits] + [
            [a, b] for a in lits for b in lits
        ]
        for _ in range(2000):
            n = rng.randint(0, 3)
            clauses = [rng.choice(clause_pool) for _ in range(n)]
            run({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

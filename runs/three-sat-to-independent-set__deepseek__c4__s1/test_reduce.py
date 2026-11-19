"""Tests: compare brute-force 3-SAT answers with brute-force Independent Set
answers on the reduction output, over many small instances and edge cases."""

from __future__ import annotations

import itertools
import random

import problems
from problems import IndependentSet, ThreeSat
from reduce import reduce
from solvers import independent_set_solve, three_sat_solve

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    src = three_sat_solve(instance)
    tgt = independent_set_solve(out)
    assert src == tgt, (instance, out, src, tgt)
    tests_passed += 1


def random_instance(num_vars: int, num_clauses: int, rng: random.Random) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    # Explicit edge cases
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]})
    # duplicate clauses
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # unsatisfiable
    check(
        {
            "num_vars": 3,
            "clauses": [
                [1, 2, 3],
                [1, 2, -3],
                [1, -2, 3],
                [1, -2, -3],
                [-1, 2, 3],
                [-1, 2, -3],
                [-1, -2, 3],
                [-1, -2, -3],
            ],
        }
    )

    # Exhaustive over all 3-variable formulas with up to 3 clauses
    rng = random.Random(12345)
    lits = [1, 2, 3, -1, -2, -3]
    all_clauses = []
    for combo in itertools.combinations(range(6), 3):
        if len({abs(lits[i]) for i in combo}) == 3:
            all_clauses.append([lits[i] for i in combo])
    for nclauses in range(0, 4):
        for clauses in itertools.combinations_with_replacement(all_clauses, nclauses):
            check({"num_vars": 3, "clauses": [list(c) for c in clauses]})

    # Random small instances
    for _ in range(3000):
        num_vars = rng.randint(0, 5)
        num_clauses = rng.randint(0, 6)
        if num_clauses > 0:
            num_vars = max(num_vars, 3)
        check(random_instance(num_vars, num_clauses, rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

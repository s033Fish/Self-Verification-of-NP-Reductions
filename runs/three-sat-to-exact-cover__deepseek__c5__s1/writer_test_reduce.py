"""Tests comparing brute-force answers of source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, ExactCover
from reduce import reduce
from solvers import solve_three_sat, solve_exact_cover

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    ExactCover.validate(reduced)
    a = solve_three_sat(instance)
    b = solve_exact_cover(reduced)
    if a != b:
        raise AssertionError(
            f"MISMATCH: source={instance} source_answer={a} "
            f"reduced={reduced} reduced_answer={b}"
        )
    TESTS_PASSED += 1


def all_3sat_instances(num_vars: int, max_clauses: int):
    """All 3-SAT instances over num_vars with up to max_clauses clauses."""
    literals = []
    for v in range(1, num_vars + 1):
        literals.append(v)
        literals.append(-v)
    # All valid clauses: 3 distinct variables, no v and -v together.
    clauses = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    # Include all multisets of clauses up to max_clauses (with repetition).
    for r in range(0, max_clauses + 1):
        for chosen in itertools.combinations_with_replacement(clauses, r):
            yield {"num_vars": num_vars, "clauses": [list(c) for c in chosen]}


def main() -> None:
    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})

    # Exhaustive small instances.
    for inst in all_3sat_instances(3, 2):
        check(inst)
    for inst in all_3sat_instances(4, 1):
        check(inst)

    # Random instances of various sizes.
    rng = random.Random(12345)
    for _ in range(3000):
        m = rng.randint(3, 7)
        n = rng.randint(0, 8)
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v * rng.choice([1, -1]) for v in vs]
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses})

    # Random instances biased toward satisfiable / unsatisfiable.
    for _ in range(1500):
        m = rng.randint(3, 6)
        n = rng.randint(1, 10)
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v * rng.choice([1, -1]) for v in vs]
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses})

    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, 3]]})

    # Known unsat: all 8 clauses over 3 vars.
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([s * v for s, v in zip(signs, [1, 2, 3])])
    check({"num_vars": 3, "clauses": all_clauses})

    # Variables unused in any clause.
    check({"num_vars": 6, "clauses": [[1, 2, 3]]})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")


if __name__ == "__main__":
    main()

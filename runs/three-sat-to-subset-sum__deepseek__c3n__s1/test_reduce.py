"""Tests for the 3-SAT -> Subset Sum reduction in reduce.py.

problems.py provides no solvers, so brute-force solvers for both problems
are written here from the definitions, and the reduction is checked against
them on many small instances (exhaustive-ish random sampling plus edge
cases).
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(bits[abs(lit) - 1] == (lit > 0) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums exactly to the target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation (small, valid instances).

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vars_chosen = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vars_chosen]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat(max_vars: int = 4, max_clauses: int = 3):
    """Yield a deterministic collection of small valid 3-SAT instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        # all possible clauses over variables 1..m
        clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                clauses.append([s * v for s, v in zip(signs, vs)])
        # empty formula, single clauses, and random-ish subsets
        yield {"num_vars": m, "clauses": []}
        for c in clauses:
            yield {"num_vars": m, "clauses": [list(c)]}
        for size in range(2, max_clauses + 1):
            for _ in range(40):
                rng = random.Random(f"{m}-{size}-{len(clauses)}")
                chosen = [list(c) for c in rng.sample(clauses, min(size, len(clauses)))]
                yield {"num_vars": m, "clauses": chosen}


# ----------------------------------------------------------------------
# Tests

def check_instance(instance: dict) -> None:
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, reduced={got}, "
        f"reduction={reduced}"
    )


def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def case(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check_instance(instance)
        tests_passed += 1

    # 1. Explicit edge cases.
    case({"num_vars": 0, "clauses": []})
    case({"num_vars": 1, "clauses": []})
    case({"num_vars": 5, "clauses": []})
    # unsatisfiable: all 8 clauses over 3 variables
    case({"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ]})
    # trivially satisfiable single clause
    case({"num_vars": 3, "clauses": [[1, 2, 3]]})
    # duplicate clauses
    case({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # unused variables
    case({"num_vars": 6, "clauses": [[1, 2, 3]]})

    # 2. Deterministic small-instance sweep.
    for instance in all_small_three_sat():
        case(instance)

    # 3. Random sampling.
    rng = random.Random(12345)
    for _ in range(400):
        case(random_three_sat(rng, max_vars=5, max_clauses=6))

    return tests_run, tests_passed


if __name__ == "__main__":
    total, passed = run_tests()
    print(f"tests_run={total} tests_passed={passed}")
    assert total == passed
    print("ALL TESTS PASSED")

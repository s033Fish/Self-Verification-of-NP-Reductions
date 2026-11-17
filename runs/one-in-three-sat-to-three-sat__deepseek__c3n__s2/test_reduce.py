"""Tests for the 1-in-3-SAT -> 3-SAT reduction.

Includes brute-force solvers written from the problem definitions, plus a
randomised equivalence test over many small source instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions


def solve_one_in_three(instance: dict) -> bool:
    """True iff some assignment makes exactly one variable true per clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(sum(1 for v in clause if bits[v - 1]) == 1 for clause in clauses):
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause (>= 1 true literal)."""
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


# ----------------------------------------------------------------------
# Helpers


def random_source(rng: random.Random) -> dict:
    """A random small, valid 1-in-3-SAT instance."""
    m = rng.randint(0, 4)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, 4)):
            a, b, c = rng.sample(range(1, m + 1), 3)
            clauses.append([a, b, c])
    return {"num_vars": m, "clauses": clauses}


def check(instance: dict) -> bool:
    """Validate, reduce, validate the result, and compare answers."""
    problems.OneInThreeSat.validate(instance)
    target = reduce(instance)
    problems.ThreeSat.validate(target)
    src = solve_one_in_three(instance)
    tgt = solve_three_sat(target)
    assert src == tgt, (instance, target, src, tgt)
    return True


# ----------------------------------------------------------------------
# Tests


def test_edge_cases() -> int:
    run = 0
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},  # duplicates
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [1, 4, 5]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4], [1, 3, 4]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
    ]
    for case in cases:
        check(case)
        run += 1
    return run


def test_all_small() -> int:
    """Exhaustively test clause multisets (size <= 3) on 3 and 4 variables."""
    run = 0
    for m in (3, 4):
        triples = list(itertools.combinations(range(1, m + 1), 3))
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(triples, r):
                instance = {"num_vars": m, "clauses": [list(t) for t in combo]}
                check(instance)
                run += 1
    return run


def test_random() -> int:
    rng = random.Random(12345)
    run = 0
    for _ in range(400):
        check(random_source(rng))
        run += 1
    return run


def test_random_larger() -> int:
    """Random instances with up to 6 source vars and few clauses."""
    rng = random.Random(999)
    run = 0
    for _ in range(200):
        m = rng.randint(3, 6)
        clauses = []
        for _ in range(rng.randint(0, 2)):
            a, b, c = rng.sample(range(1, m + 1), 3)
            clauses.append([a, b, c])
        check({"num_vars": m, "clauses": clauses})
        run += 1
    return run


def test_no_mutation_and_size() -> int:
    """reduce must not mutate its input and must be linear-sized."""
    run = 0
    instance = {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]}
    import copy
    snapshot = copy.deepcopy(instance)
    target = reduce(instance)
    assert instance == snapshot, "reduce mutated its input"
    assert target["num_vars"] == 4 + 3 * len(instance["clauses"])
    assert len(target["clauses"]) == 7 * len(instance["clauses"])
    run += 1
    return run


def main() -> None:
    total = 0
    passed = 0
    for name, fn in [
        ("edge_cases", test_edge_cases),
        ("all_small", test_all_small),
        ("random", test_random),
        ("random_larger", test_random_larger),
        ("no_mutation_and_size", test_no_mutation_and_size),
    ]:
        n = fn()
        total += n
        passed += n
        print(f"{name}: {n} checks passed")
    print(f"TOTAL: {passed}/{total} passed")
    assert passed == total


if __name__ == "__main__":
    main()

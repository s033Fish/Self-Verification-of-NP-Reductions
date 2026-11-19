"""Tests comparing brute-force answers on source instances and reductions."""
from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat
from solvers import three_sat_solve, nae_three_sat_solve
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    NaeThreeSat.validate(out)
    expected = three_sat_solve(instance)
    got = nae_three_sat_solve(out)
    assert got == expected, (instance, out, expected, got)
    TESTS_PASSED += 1


def random_instance(rng, max_vars=5, max_clauses=4):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small():
    # all formulas with m=3, up to 3 clauses over all possible clauses
    all_clauses = []
    for vs in itertools.combinations(range(1, 4), 3):
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([v * s for v, s in zip(vs, signs)])
    for k in range(0, 4):
        for combo in itertools.combinations(all_clauses, k):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]})


def edge_cases():
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]})


def main():
    exhaustive_small()
    edge_cases()
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, max_vars=6, max_clauses=5))
    extra_stress()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")



def extra_stress():
    # all 8 clauses over 3 vars -> unsatisfiable
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([1 * signs[0], 2 * signs[1], 3 * signs[2]])
    check({"num_vars": 3, "clauses": [list(c) for c in all_clauses]})
    # 7 of 8 -> still unsat? (3-SAT: all 8 needed for unsat over 3 vars)
    for drop in range(8):
        check({"num_vars": 3, "clauses": [list(c) for i, c in enumerate(all_clauses) if i != drop]})
    rng = random.Random(999)
    for _ in range(4000):
        check(random_instance(rng, max_vars=7, max_clauses=8))
    # larger sparse instances
    for _ in range(500):
        m = rng.randint(3, 9)
        clauses = []
        for _ in range(rng.randint(0, 12)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        check({"num_vars": m, "clauses": clauses})

if __name__ == "__main__":
    main()

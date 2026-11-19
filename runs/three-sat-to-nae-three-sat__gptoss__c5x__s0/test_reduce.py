"""Independent tests for reduce.py (3-SAT -> NAE-3-SAT).

We brute-force both problems with solvers.py and check that, for many small
source instances, the source answer equals the target answer of the reduction.
"""

from __future__ import annotations

import random
from itertools import combinations, combinations_with_replacement, product

from solvers import solve_three_sat, solve_nae_three_sat
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(instance, label=""):
    """Compare source answer with the target answer of the reduction."""
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    src = solve_three_sat(instance)
    reduced = reduce(instance)
    tgt = solve_nae_three_sat(reduced)
    if src == tgt:
        TESTS_PASSED += 1
        return True
    FAILURES.append((label, instance, src, reduced, tgt))
    return False


def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m."""
    out = []
    for vs in combinations(range(1, m + 1), 3):
        for signs in product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, vs)])
    return out


def test_edge_cases():
    # No clauses is yes for both, for any m including 0.
    for m in range(0, 5):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")


def test_exhaustive():
    # Exhaustively enumerate multisets of clauses up to a small size.
    for m in (3, 4):
        cls = all_clauses(m)
        max_r = 3 if m == 3 else 2
        for r in range(1, max_r + 1):
            for combo in combinations_with_replacement(range(len(cls)), r):
                inst = {"num_vars": m, "clauses": [cls[i] for i in combo]}
                check(inst, f"exhaustive m={m} r={r}")


def test_random():
    rng = random.Random(12345)
    for m in range(3, 8):
        cls = all_clauses(m)
        for _ in range(300):
            r = rng.randint(1, 8)
            inst = {"num_vars": m, "clauses": [list(rng.choice(cls)) for _ in range(r)]}
            check(inst, f"random m={m}")


def test_known_counterexample():
    # Forces x=1 true; then clause (1,2,3) has all literals true in every
    # satisfying assignment, so no auxiliary value can satisfy both NAE clauses.
    inst = {"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
    ]}
    check(inst, "forced-all-true counterexample")


def main():
    test_edge_cases()
    test_exhaustive()
    test_random()
    test_known_counterexample()

    print(f"tests_run    = {TESTS_RUN}")
    print(f"tests_passed = {TESTS_PASSED}")
    print(f"failures     = {len(FAILURES)}")
    for label, inst, src, reduced, tgt in FAILURES[:5]:
        print("---")
        print("label  :", label)
        print("source :", inst, "->", src)
        print("reduced:", reduced, "->", tgt)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    raise SystemExit(main())

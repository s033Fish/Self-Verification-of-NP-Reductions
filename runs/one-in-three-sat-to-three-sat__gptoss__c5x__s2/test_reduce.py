"""Independent tests for reduce.py (1-in-3-SAT -> 3-SAT).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answers of many small source
instances with the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random
import time

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_one_in_three_sat(instance):
    """Return True iff some assignment makes exactly one var true per clause."""
    problems.OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for (a, b, c) in clauses:
            # variables are 1..m
            if (bits[a - 1] + bits[b - 1] + bits[c - 1]) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance):
    """Return True iff some assignment satisfies every clause (>=1 true lit)."""
    problems.ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and bits[lit - 1]) or (lit < 0 and not bits[-lit - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation (small, exhaustive-ish + random).


def all_source_instances(max_m=4, max_clauses=3):
    """Yield a broad set of small, valid source instances."""
    for m in range(0, max_m + 1):
        # all possible clauses over 1..m (positive, 3 distinct vars)
        possible = [
            list(c)
            for c in itertools.combinations(range(1, m + 1), 3)
        ]
        if not possible:
            yield {"num_vars": m, "clauses": []}
            continue
        for k in range(0, max_clauses + 1):
            for combo in itertools.combinations_with_replacement(possible, k):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def random_source_instances(rng, count, max_m=7, max_clauses=8):
    for _ in range(count):
        m = rng.randint(0, max_m)
        possible = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        if not possible:
            yield {"num_vars": m, "clauses": []}
            continue
        k = rng.randint(0, max_clauses)
        clauses = [list(rng.choice(possible)) for _ in range(k)]
        # sometimes shuffle literal order
        for cl in clauses:
            rng.shuffle(cl)
        rng.shuffle(clauses)
        yield {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src_ans = solve_one_in_three_sat(instance)
        reduced = reduce(instance)
        # target must validate
        problems.ThreeSat.validate(reduced)
        tgt_ans = solve_three_sat(reduced)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, src_ans, tgt_ans))

    # Exhaustive small instances.
    for inst in all_source_instances(max_m=4, max_clauses=3):
        check(inst, "exhaustive")

    # Random larger instances.
    rng = random.Random(12345)
    for inst in random_source_instances(rng, 4000, max_m=7, max_clauses=8):
        check(inst, "random")

    # Edge cases explicitly.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "dup clause")

    # Timing sanity: reduction must be polynomial / fast.
    big = {"num_vars": 200, "clauses": [[i, i + 1, i + 2] for i in range(1, 199)]}
    t0 = time.time()
    out = reduce(big)
    dt = time.time() - t0
    assert len(out["clauses"]) == 5 * len(big["clauses"])

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    print(f"big reduction time={dt:.4f}s clauses={len(out['clauses'])}")
    if failures:
        print("FAILURES:")
        for label, inst, reduced, s, t in failures[:10]:
            print(label, inst, "->", reduced, "src", s, "tgt", t)
    else:
        print("ALL MATCH")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()

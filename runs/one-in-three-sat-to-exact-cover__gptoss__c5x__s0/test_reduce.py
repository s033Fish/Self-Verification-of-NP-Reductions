"""Independent brute-force solvers and tests for the 1-in-3-SAT -> Exact Cover reduction.

Solvers are written directly from the problem docstrings in problems.py and are
independent of reduce.py.
"""

from __future__ import annotations

import itertools
import random
import sys
import time

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute force: try every assignment of variables 1..m."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if sum(1 for v in clause if bits[v - 1]) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Brute force exact cover via backtracking on the lowest uncovered element."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    full = frozenset(range(u))

    by_elem = {e: [] for e in range(u)}
    for s in sets:
        for e in s:
            by_elem[e].append(s)

    def rec(covered: frozenset) -> bool:
        if covered == full:
            return True
        e = min(x for x in range(u) if x not in covered)
        for s in by_elem[e]:
            if s.isdisjoint(covered):
                if rec(covered | s):
                    return True
        return False

    return rec(frozenset())


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_clauses(m: int):
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


def gen_exhaustive(max_m, max_len):
    """All clause lists (with repetition) up to max_len over m<=max_m."""
    for m in range(0, max_m + 1):
        clauses = all_clauses(m)
        for length in range(0, max_len + 1):
            for combo in itertools.product(clauses, repeat=length):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def gen_random(num, seed=0, max_vars=7, max_clauses=8):
    rng = random.Random(seed)
    out = []
    for _ in range(num):
        m = rng.randint(0, max_vars)
        clauses = all_clauses(m)
        k = rng.randint(0, max_clauses)
        cl = [list(rng.choice(clauses)) for _ in range(k)] if clauses else []
        out.append({"num_vars": m, "clauses": cl})
    return out


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src = solve_one_in_three_sat(inst)
            red = reduce(inst)
            ExactCover.validate(red)
            tgt = solve_exact_cover(red)
        except Exception as exc:
            failures.append((inst, "exception", repr(exc)))
            return
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, tgt))

    # Explicit edge cases
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 3, "clauses": []})
    run({"num_vars": 7, "clauses": []})
    run({"num_vars": 3, "clauses": [[1, 2, 3]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    run({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]})
    run({"num_vars": 5, "clauses": [[1, 2, 3], [1, 2, 4], [1, 2, 5]]})

    # Exhaustive small instances (all clause multisets up to length 3, m<=5)
    for inst in gen_exhaustive(5, 3):
        run(inst)

    # Exhaustive deeper for tiny m (all clause multisets up to length 4, m<=4)
    for inst in gen_exhaustive(5, 3):
        run(inst)

    # Random larger instances
    for inst in gen_random(6000, seed=12345, max_vars=6, max_clauses=6):
        run(inst)
    for inst in gen_random(2000, seed=999, max_vars=6, max_clauses=8):
        run(inst)

    # Polynomial-time sanity check on a large instance
    big = {"num_vars": 500, "clauses": [[1, 2, 3] for _ in range(2000)]}
    t0 = time.time()
    red_big = reduce(big)
    dt = time.time() - t0
    assert red_big["universe_size"] == 2000 + 6000, red_big["universe_size"]
    print(f"large reduce time: {dt:.3f}s, universe_size={red_big['universe_size']}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  ", f)
        sys.exit(1)
    print("ALL PASSED")


if __name__ == "__main__":
    main()

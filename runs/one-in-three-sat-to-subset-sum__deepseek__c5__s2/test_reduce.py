"""Independent review of reduce.py: 1-in-3-SAT (positive) -> Subset Sum.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_one_in_three_sat(instance):
    """Yes iff some assignment makes exactly one var true in every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            cnt = sum(1 for v in clause if bits[v - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    """Yes iff some sub-list sums to target."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in instance["numbers"]:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation (valid source instances).

def random_source_instance(rng, max_vars=6, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        c = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(c):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append(vs)
    return {"num_vars": m, "clauses": clauses}


def all_source_instances(max_vars=4, max_clauses=3):
    """Exhaustive-ish small enumeration over distinct variable sets."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        triples = list(itertools.combinations(range(1, m + 1), 3))
        # all subsets of triples up to max_clauses, with orderings
        for k in range(0, min(max_clauses, len(triples)) + 1):
            for combo in itertools.combinations(triples, k):
                for perm in itertools.permutations(combo):
                    yield {"num_vars": m, "clauses": [list(t) for t in perm]}


# ----------------------------------------------------------------------
# Tests.

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(src):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate source
        OneInThreeSat.validate(src)
        expected = solve_one_in_three_sat(src)
        tgt = reduce(src)
        # validate target
        SubsetSum.validate(tgt)
        got = solve_subset_sum(tgt)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((src, tgt, expected, got))

    # Edge cases explicitly.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})

    # Exhaustive small enumeration.
    for src in all_source_instances(max_vars=4, max_clauses=3):
        check(src)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(4000):
        src = random_source_instance(rng, max_vars=7, max_clauses=8)
        check(src)

    # Random with duplicated clauses and unused vars.
    for _ in range(2000):
        m = rng.randint(3, 6)
        c = rng.randint(0, 8)
        clauses = [rng.sample(range(1, m + 1), 3) for _ in range(c)]
        check({"num_vars": m, "clauses": clauses})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for src, tgt, expected, got in failures[:5]:
            print("  src=", src, "expected=", expected, "got=", got, "tgt=", tgt)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run()

"""Independent brute-force verification of reduce.py.

SOURCE = 1-in-3-SAT (positive), TARGET = Exact Cover.
Solvers below are written directly from the docstring definitions in
problems.py; they are NOT used by reduce.py.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions.

def solve_one_in_three_sat(instance: dict) -> bool:
    """Yes iff some assignment makes exactly one var true in every clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(sum(1 for v in clause if bits[v - 1]) == 1 for clause in clauses):
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Yes iff some subcollection of sets is a disjoint cover of the universe."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    fs = [frozenset(s) for s in instance["sets"]]
    full = frozenset(range(u))
    for mask in range(1 << len(fs)):
        union = frozenset()
        ok = True
        for i, s in enumerate(fs):
            if (mask >> i) & 1:
                if union & s:
                    ok = False
                    break
                union |= s
        if ok and union == full:
            return True
    return False


# ----------------------------------------------------------------------
# One check: reduction must preserve the answer and produce a valid target.

def check(instance: dict) -> bool:
    src = solve_one_in_three_sat(instance)
    target = reduce(instance)
    ExactCover.validate(target)          # target instance must be well-formed
    return src == solve_exact_cover(target)


def _record(inst, stats):
    stats["total"] += 1
    if check(inst):
        stats["passed"] += 1
    else:
        stats["failures"].append(inst)


# ----------------------------------------------------------------------
# Test suites

def exhaustive_small(stats):
    """All instances with m in 0..4 and up to 3 clauses (with repetition)."""
    for m in range(0, 5):
        vc = list(itertools.combinations(range(1, m + 1), 3))
        for c in range(0, 4):
            if c > 0 and m < 3:
                continue
            for combo in itertools.combinations_with_replacement(vc, c):
                _record({"num_vars": m, "clauses": [list(x) for x in combo]}, stats)


def random_tests(stats, per_seed=500, seeds=20):
    """Random instances, several seeds, larger sizes."""
    for seed in range(seeds):
        rng = random.Random(seed)
        for _ in range(per_seed):
            m = rng.randint(0, 8)
            c = rng.randint(0, 8)
            clauses = []
            for _ in range(c):
                if m < 3:
                    break
                clauses.append(rng.sample(range(1, m + 1), 3))
            _record({"num_vars": m, "clauses": clauses}, stats)


def explicit_edge_cases(stats):
    cases = [
        ({"num_vars": 0, "clauses": []}, True),                 # empty, m=0
        ({"num_vars": 3, "clauses": []}, True),                 # no clauses
        ({"num_vars": 3, "clauses": [[1, 2, 3]]}, True),
        ({"num_vars": 3, "clauses": [[1, 2, 3]] * 2}, True),    # duplicate clause
        ({"num_vars": 3, "clauses": [[1, 2, 3]] * 5}, True),
        ({"num_vars": 5, "clauses": [[1, 2, 3]]}, True),        # unused vars
        ({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4],
                                     [1, 3, 4], [2, 3, 4]]}, False),  # unsat
    ]
    for inst, expected in cases:
        stats["total"] += 1
        got = solve_one_in_three_sat(inst)
        if got != expected:
            stats["failures"].append(("source-solver-wrong", inst, got, expected))
            continue
        if check(inst):
            stats["passed"] += 1
        else:
            stats["failures"].append(inst)


def main():
    stats = {"total": 0, "passed": 0, "failures": []}
    for fn in (exhaustive_small, random_tests, explicit_edge_cases):
        fn(stats)
    print(f"tests_run={stats['total']} tests_passed={stats['passed']}")
    if stats["failures"]:
        print("FAILURES:")
        for f in stats["failures"][:20]:
            print("  ", f)
    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": not stats["failures"] and stats["total"] == stats["passed"],
                "tests_run": stats["total"],
                "tests_passed": stats["passed"],
            },
            fh,
        )
        fh.write("\n")
    return stats


if __name__ == "__main__":
    main()

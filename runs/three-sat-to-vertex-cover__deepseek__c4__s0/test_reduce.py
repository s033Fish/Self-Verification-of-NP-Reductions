"""Tests comparing brute-force answers on 3-SAT instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce
from solvers import solve_three_sat, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    expected = solve_three_sat(instance)
    target = reduce(instance)
    VertexCover.validate(target)
    got = solve_vertex_cover(target)
    if got == expected:
        tests_passed += 1
    else:
        print("FAIL", label, instance, "expected", expected, "got", got, "target", target)
        raise AssertionError(f"mismatch on {instance}")


def all_clauses(m):
    """All possible clauses (3 distinct vars, no var repeated)."""
    result = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            result.append([s * v for s, v in zip(signs, vars_)])
    return result


def extra():
    """Larger random instances."""
    rng = random.Random(999)
    for trial in range(40):
        m = rng.randint(6, 7)
        allc = all_clauses(m)
        chosen = [list(c) for c in rng.sample(allc, rng.randint(0, 8))]
        check({"num_vars": m, "clauses": chosen}, f"extra {trial}")
    # Known unsat: all 8 clauses over 3 vars.
    allc3 = [list(c) for c in all_clauses(3)]
    check({"num_vars": 3, "clauses": allc3}, "all 8 clauses unsat")
    # Known sat.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "known sat")


def main():
    # Edge case: no clauses, m = 0.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    # Edge case: no clauses, various m.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []}, f"no clauses m={m}")

    # Exhaustive: m = 3, all subsets of the 8 possible clauses up to size 3.
    clauses3 = all_clauses(3)
    for size in range(0, 4):
        for combo in itertools.combinations(clauses3, size):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]},
                  f"m=3 size={size}")

    # Exhaustive: m = 4, all single clauses and all pairs of clauses.
    clauses4 = all_clauses(4)
    for c in clauses4:
        check({"num_vars": 4, "clauses": [list(c)]}, "m=4 single")
    for combo in itertools.combinations(clauses4, 2):
        check({"num_vars": 4, "clauses": [list(c) for c in combo]}, "m=4 pair")

    # Random small instances.
    rng = random.Random(12345)
    for trial in range(400):
        m = rng.randint(3, 6)
        allc = all_clauses(m)
        num_clauses = rng.randint(0, min(8, len(allc)))
        chosen = [list(c) for c in rng.sample(allc, num_clauses)]
        check({"num_vars": m, "clauses": chosen}, f"random {trial}")

    # Duplicate clauses and unused variables.
    for trial in range(100):
        m = rng.randint(3, 6)
        allc = all_clauses(m)
        chosen = [list(rng.choice(allc)) for _ in range(rng.randint(0, 6))]
        check({"num_vars": m, "clauses": chosen}, f"dup {trial}")

    extra()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()

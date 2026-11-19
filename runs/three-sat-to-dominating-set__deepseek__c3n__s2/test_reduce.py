"""Tests for the 3-SAT -> Dominating Set reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, DominatingSet
from reduce import reduce
from solvers import solve_three_sat, solve_dominating_set

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance, label=""):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeSat.validate(instance)
    target = reduce(instance)
    DominatingSet.validate(target)
    expected = solve_three_sat(instance)
    got = solve_dominating_set(target)
    if expected == got:
        TESTS_PASSED += 1
    else:
        raise AssertionError(
            f"mismatch {label}: src={instance} expected={expected} "
            f"target={target} got={got}"
        )


def all_clauses(num_vars):
    """All valid 3-clauses over variables 1..num_vars."""
    result = []
    for vars_ in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            result.append([s * v for s, v in zip(signs, vars_)])
    return result


def brute_ds(instance):
    """Independent brute force for cross-checking solve_dominating_set."""
    n = instance["n"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    closed = [adj[i] | {i} for i in range(n)]
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set()
            for v in subset:
                covered |= closed[v]
            if len(covered) == n:
                return True
    return False


def main():
    # --- Sanity-check the DS solver against brute force on random graphs ---
    rng = random.Random(999)
    for _ in range(300):
        n = rng.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(possible)
        edges = [list(e) for e in possible[: rng.randint(0, len(possible))]]
        inst = {"n": n, "edges": edges, "k": rng.randint(-1, n + 1)}
        a = solve_dominating_set(inst)
        b = brute_ds(inst)
        assert a == b, (inst, a, b)
    print("solver cross-check ok")

    # --- Edge cases: no clauses, any m (including m = 0) ---
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # --- All formulas over 3 variables with up to 2 clauses ---
    clauses3 = all_clauses(3)
    for r in range(0, 3):
        for combo in itertools.combinations_with_replacement(clauses3, r):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]},
                  f"m=3 r={r}")

    # --- Unsatisfiable instance: all 8 clauses over 3 variables ---
    check({"num_vars": 3, "clauses": [list(c) for c in clauses3]}, "unsat m=3")

    # --- Random small instances over 3..4 variables, few clauses ---
    rng = random.Random(12345)
    for m in range(3, 5):
        pool = all_clauses(m)
        for _ in range(150):
            c = rng.randint(0, 4)
            clauses = [list(rng.choice(pool)) for _ in range(c)]
            check({"num_vars": m, "clauses": clauses}, f"random m={m}")

    # --- Duplicate clauses ---
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
          "duplicates")

    # --- Unused variables ---
    check({"num_vars": 5, "clauses": [[1, 2, 3]]}, "unused vars")

    # --- Literal order / clause order invariance ---
    check({"num_vars": 3, "clauses": [[3, -1, 2]]}, "literal order")

    extra()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED
    return TESTS_RUN, TESTS_PASSED




def extra():
    global TESTS_RUN, TESTS_PASSED
    # Exhaustive: all 3-var formulas with up to 4 clauses.
    clauses3 = all_clauses(3)
    for r in range(0, 5):
        for combo in itertools.combinations_with_replacement(clauses3, r):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]}, f"exh3 r={r}")
    # Exhaustive: all 4-var formulas with up to 2 clauses.
    clauses4 = all_clauses(4)
    for r in range(0, 3):
        for combo in itertools.combinations_with_replacement(clauses4, r):
            check({"num_vars": 4, "clauses": [list(c) for c in combo]}, f"exh4 r={r}")
    # Adversarial: clause vertices cover all literals (potential substitute).
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]}, "cover-all")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4], [-1, 2, -4]]}, "cover-all4")
    # Random 4-var with many clauses.
    rng = random.Random(777)
    for _ in range(300):
        c = rng.randint(0, 10)
        clauses = [list(rng.choice(clauses4)) for _ in range(c)]
        check({"num_vars": 4, "clauses": clauses}, "rand4")
    print(f"extra tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()

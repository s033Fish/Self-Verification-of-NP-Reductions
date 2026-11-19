"""Independent tests for reduce.py (3-SAT -> 3-Coloring).

We implement brute-force solvers for both problems from the definitions in
problems.py, then compare the answer of many small source instances with the
answer of their reductions.
"""

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def sat_solve(instance):
    """True iff some assignment satisfies every 3-literal clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def color_solve(instance):
    """True iff the graph is properly 3-colourable."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colors = [-1] * n

    def backtrack(i):
        if i == n:
            return True
        for c in range(3):
            if all(colors[j] != c for j in adj[i]):
                colors[i] = c
                if backtrack(i + 1):
                    return True
                colors[i] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    expected = sat_solve(instance)
    graph = reduce(instance)
    got = color_solve(graph)
    if expected == got:
        tests_passed += 1
    else:
        failures.append((label, instance, expected, got, graph))


def all_clauses(m):
    """All distinct 3-literal clauses on 3 different variables of 1..m."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([v * s for v, s in zip(vars_, signs)])
    return clauses


def main():
    random.seed(12345)

    # 1. Formulas with no clauses: satisfiable for any m.
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # 2. Exhaustive over every subset of clauses for m = 3 (256 instances).
    clauses3 = all_clauses(3)
    for mask in range(1 << len(clauses3)):
        subset = [clauses3[i] for i in range(len(clauses3)) if (mask >> i) & 1]
        check({"num_vars": 3, "clauses": subset}, f"m=3 mask={mask}")

    # 3. Random formulas for m = 4, 5, 6.
    for m in (4, 5, 6):
        pool = all_clauses(m)
        for trial in range(300):
            k = random.randint(0, min(len(pool), 10))
            subset = random.sample(pool, k)
            check({"num_vars": m, "clauses": subset}, f"random m={m} trial={trial}")

    # 4. Explicit counterexample found by inspection: a satisfiable formula
    #    that forces x1 = x2 = x3 = True, so the clause (x1 v x2 v x3) has all
    #    literals true.  The gadget then forces the clause triangle to use only
    #    the two non-TRUE colours -> uncolorable.
    clauses = []
    for x in (1, 2, 3):
        for sy in (4, -4):
            for sz in (5, -5):
                clauses.append([x, sy, sz])
    clauses.append([1, 2, 3])
    check({"num_vars": 5, "clauses": clauses}, "explicit counterexample")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, expected, got, graph in failures[:5]:
            print(f"  {label}: sat={expected} color={got}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

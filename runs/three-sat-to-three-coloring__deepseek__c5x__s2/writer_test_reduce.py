"""Tests for the 3-SAT -> 3-Coloring reduction.

Contains brute-force solvers for both problems (from the definitions in
problems.py) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def sat_solve(instance):
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def coloring_solve(instance):
    """True iff the graph is 3-colourable (brute force over 3^n)."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colours = [0] * n

    def rec(i):
        if i == n:
            return True
        for c in range(3):
            if all(colours[j] != c for j in adj[i] if j < i):
                colours[i] = c
                if rec(i + 1):
                    return True
                colours[i] = 0
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance helpers


def make_formula(num_vars, clauses):
    return {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


def all_clauses(num_vars):
    out = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, combo)])
    return out


def random_formula(rng, max_vars=4, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        pool = all_clauses(m)
        k = rng.randint(0, max_clauses)
        for _ in range(k):
            clauses.append(list(rng.choice(pool)))
    return make_formula(m, clauses)


# ----------------------------------------------------------------------
# Tests


def check(instance, results):
    results["run"] += 1
    ThreeSat.validate(instance)
    expected = sat_solve(instance)
    target = reduce(instance)
    ThreeColoring.validate(target)
    got = coloring_solve(target)
    if got == expected:
        results["passed"] += 1
    else:
        results["failures"].append((instance, expected, got, target))


def main():
    rng = random.Random(12345)
    results = {"run": 0, "passed": 0, "failures": []}

    # Edge cases: no clauses, various m (including m = 0).
    for m in range(0, 6):
        check(make_formula(m, []), results)

    # Small exhaustive-ish set of formulas over 3 variables.
    for r in range(0, 4):
        for clauses in itertools.combinations(all_clauses(3), r):
            check(make_formula(3, clauses), results)

    # All 8 clauses over 3 variables -> unsatisfiable.
    check(make_formula(3, all_clauses(3)), results)

    # Random formulas.
    for _ in range(600):
        check(random_formula(rng), results)

    # A few larger random ones (still brute-forceable).
    for _ in range(60):
        check(random_formula(rng, max_vars=5, max_clauses=8), results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    for inst, exp, got, target in results["failures"][:5]:
        print("FAIL", inst, "expected", exp, "got", got, "target", target)
    assert not results["failures"], "some tests failed"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

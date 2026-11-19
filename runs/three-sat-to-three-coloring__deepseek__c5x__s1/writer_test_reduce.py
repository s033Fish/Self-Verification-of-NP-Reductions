"""Tests for reduce.py: compare brute-force answers on source instances with
brute-force answers on their reductions."""

from __future__ import annotations

import itertools
import random
import sys

from problems import ThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)


def sat_solve(instance) -> bool:
    """Brute force 3-SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def color_solve(instance) -> bool:
    """Backtracking 3-colouring solver with degree-based ordering."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    colour = [-1] * n
    # Order vertices by decreasing degree to fail fast.
    order = sorted(range(n), key=lambda x: -len(adj[x]))

    def bt(idx: int) -> bool:
        if idx == n:
            return True
        u = order[idx]
        used = {colour[j] for j in adj[u] if colour[j] != -1}
        for c in range(3):
            if c not in used:
                colour[u] = c
                if bt(idx + 1):
                    return True
                colour[u] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generators


def clauses_over(m: int):
    """All possible 3-literal clauses over variables 1..m."""
    if m < 3:
        return []
    out = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([signs[i] * combo[i] for i in range(3)])
    return out


def exhaustive_three_sat_instances(max_vars: int, max_clauses: int):
    """Yield small valid 3-SAT instances exhaustively (bounded)."""
    for m in range(0, max_vars + 1):
        if m == 0:
            yield {"num_vars": 0, "clauses": []}
            continue
        clauses = clauses_over(m)
        yield {"num_vars": m, "clauses": []}
        for clause in clauses:
            yield {"num_vars": m, "clauses": [clause]}
        for i in range(len(clauses)):
            for j in range(i, len(clauses)):
                yield {"num_vars": m, "clauses": [clauses[i], clauses[j]]}
        if max_clauses >= 3 and m <= 3 and len(clauses) <= 8:
            for combo in itertools.combinations_with_replacement(
                range(len(clauses)), 3
            ):
                yield {"num_vars": m, "clauses": [clauses[c] for c in combo]}


def random_three_sat_instances(count: int, max_vars: int, max_clauses: int,
                               seed: int = 12345):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        m = rng.randint(0, max_vars)
        k = 0 if m < 3 else rng.randint(0, max_clauses)
        clauses = []
        for _ in range(k):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        out.append({"num_vars": m, "clauses": clauses})
    return out


# ----------------------------------------------------------------------
# Tests


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        ThreeColoring.validate(reduced)
        expected = sat_solve(instance)
        got = color_solve(reduced)
        if expected != got:
            print("MISMATCH", instance, "expected", expected, "got", got,
                  "graph", reduced)
            raise AssertionError("mismatch")
        tests_passed += 1

    # 1. Exhaustive small instances (m up to 4, up to 3 clauses).
    for inst in exhaustive_three_sat_instances(max_vars=4, max_clauses=3):
        check(inst)

    # 2. Random instances of various sizes.
    for inst in random_three_sat_instances(300, max_vars=5, max_clauses=8,
                                           seed=1):
        check(inst)
    for inst in random_three_sat_instances(150, max_vars=6, max_clauses=10,
                                           seed=2):
        check(inst)
    for inst in random_three_sat_instances(80, max_vars=6, max_clauses=12,
                                           seed=3):
        check(inst)

    # 3. Explicit edge cases.
    check({"num_vars": 0, "clauses": []})          # yes
    check({"num_vars": 5, "clauses": []})          # yes
    # all 8 clauses over 3 vars -> unsatisfiable
    check({"num_vars": 3, "clauses": clauses_over(3)})
    # duplicate clause
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    # unused variables
    check({"num_vars": 6, "clauses": [[1, 2, 3]]})
    # single clause with all negative literals
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    # tautology-ish set that is satisfiable
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3],
                                      [1, 2, -3]]})

    # 4. Structural sanity / determinism / polynomial size.
    inst = {"num_vars": 4, "clauses": [[1, -2, 3], [-1, 2, -4]]}
    r1 = reduce(inst)
    r2 = reduce(inst)
    tests_run += 1
    assert r1 == r2, "reduce must be deterministic"
    assert r1["n"] == 3 + 2 * 4 + 6 * 2, r1["n"]
    assert len(r1["edges"]) == 3 + 3 * 4 + 12 * 2, len(r1["edges"])
    tests_passed += 1

    # 5. Scaling check: n grows linearly in the number of clauses.
    tests_run += 1
    big = {"num_vars": 50,
           "clauses": [[1 + (i % 48), 2 + (i % 48), 3 + (i % 48)]
                       for i in range(100)]}
    rb = reduce(big)
    assert rb["n"] == 3 + 2 * 50 + 6 * 100
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())

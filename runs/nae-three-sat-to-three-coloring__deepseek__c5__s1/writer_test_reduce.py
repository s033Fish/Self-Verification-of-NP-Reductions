"""Tests for reduce.py: brute-force solvers + exhaustive small-instance checks."""

import itertools
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ---------------------------------------------------------------- solvers
def nae3sat_solve(instance):
    """Brute force NAE-3-SAT.  Returns True iff satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                val = bits[abs(lit) - 1]
                values.append(val if lit > 0 else not val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False  # no satisfying assignment found


def three_coloring_solve(instance):
    """Exact backtracking 3-coloring solver.  Returns True iff 3-colorable."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    # Order vertices by descending degree (helps pruning a lot).
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    colors = [-1] * n

    def bt(i):
        if i == n:
            return True
        v = order[i]
        used = 0
        for u in adj[v]:
            if colors[u] != -1:
                used |= 1 << colors[u]
        for c in range(3):
            if not (used >> c) & 1:
                colors[v] = c
                if bt(i + 1):
                    return True
                colors[v] = -1
        return False

    return bt(0)


# ---------------------------------------------------------------- helpers
def all_nae_instances(max_vars, max_clauses):
    """Yield all NAE-3-SAT instances with <= max_vars vars, <= max_clauses clauses."""
    for m in range(0, max_vars + 1):
        literals = [l for v in range(1, m + 1) for l in (v, -v)]
        clauses = []
        for a, b, c in itertools.combinations(literals, 3):
            if len({abs(a), abs(b), abs(c)}) == 3:
                clauses.append([a, b, c])
        for k in range(0, max_clauses + 1):
            for chosen in itertools.combinations(clauses, k):
                yield {"num_vars": m, "clauses": [list(c) for c in chosen]}


def check(instance):
    assert NaeThreeSat.validate(instance) is None
    target = reduce(instance)
    ThreeColoring.validate(target)
    a = nae3sat_solve(instance)
    b = three_coloring_solve(target)
    assert a == b, (instance, target, a, b)
    return a


def main():
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive small instances (all formulas with <=3 vars, <=2 clauses).
    for instance in all_nae_instances(max_vars=3, max_clauses=2):
        check(instance)
        tests_run += 1
        tests_passed += 1
    print(f"exhaustive small: {tests_run} tests passed")

    rng = random.Random(12345)

    # 2. Random instances with up to 6 vars and up to 8 clauses.
    for _ in range(3000):
        m = rng.randint(0, 6)
        if m < 3:
            clauses = []
        else:
            clauses = []
            for _ in range(rng.randint(0, 8)):
                vs = rng.sample(range(1, m + 1), 3)
                clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        instance = {"num_vars": m, "clauses": clauses}
        check(instance)
        tests_run += 1
        tests_passed += 1
    print(f"random small: {tests_run} tests passed")

    # 3. Edge cases explicitly.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3]]},
    ]
    for instance in edge_cases:
        check(instance)
        tests_run += 1
        tests_passed += 1
    print(f"edge cases: {tests_run} tests passed")

    # 4. Larger random instances (8 vars, up to 20 clauses) to stress the reduction.
    for _ in range(300):
        m = rng.randint(3, 8)
        clauses = []
        for _ in range(rng.randint(0, 20)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        check({"num_vars": m, "clauses": clauses})
        tests_run += 1
        tests_passed += 1
    print(f"larger random: {tests_run} tests passed")

    assert tests_run == tests_passed
    print(f"ALL {tests_run} TESTS PASSED")
    return tests_run, tests_passed


if __name__ == "__main__":
    tests_run, tests_passed = main()
    print(f"RESULT tests_run={tests_run} tests_passed={tests_passed}")

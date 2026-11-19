"""Independent tests for reduce.py (Clique -> SAT).

We implement our own exact solvers for Clique and SAT from the definitions in
problems.py, enumerate many small Clique instances (exhaustively for n <= 5,
plus randomized larger ones), reduce each with reduce.reduce, and check that
the two answers agree.  We also validate every produced SAT instance and check
the edge cases explicitly.
"""

from itertools import combinations
import json
import random
import sys

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Clique
# ----------------------------------------------------------------------

def solve_clique(instance):
    """Exact solver for Clique: yes iff a clique of size >= k exists."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    if k == 1:
        return n >= 1

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # A clique of size >= k exists iff some k-subset is a clique.
    for subset in combinations(range(n), k):
        ok = True
        for a, b in combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Exact solver for SAT (DPLL with unit propagation)
# ----------------------------------------------------------------------

def solve_sat(instance):
    """Exact solver for SAT: yes iff the CNF is satisfiable."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        new_clauses = []
        for clause in clauses:
            satisfied = False
            remaining = []
            for lit in clause:
                v = abs(lit)
                val = assignment.get(v)
                if val is None:
                    remaining.append(lit)
                elif (lit > 0) == val:
                    satisfied = True
                    break
            if satisfied:
                continue
            if not remaining:
                return False  # empty clause -> unsatisfiable
            new_clauses.append(remaining)

        if not new_clauses:
            return True

        # Unit propagation.
        for clause in new_clauses:
            if len(clause) == 1:
                lit = clause[0]
                v = abs(lit)
                assignment = dict(assignment)
                assignment[v] = (lit > 0)
                return dpll(new_clauses, assignment)

        # Branch on a variable.
        lit = new_clauses[0][0]
        v = abs(lit)
        for val in (True, False):
            a = dict(assignment)
            a[v] = val
            if dpll(new_clauses, a):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance enumeration
# ----------------------------------------------------------------------

def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for idx, e in enumerate(possible) if (mask >> idx) & 1]
        yield edges


def check(instance, expected, stats, failures):
    """Reduce, validate, solve and compare a single instance."""
    Clique.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    got = solve_sat(reduced)
    stats["run"] += 1
    if got == expected:
        stats["passed"] += 1
    else:
        failures.append((instance, expected, got, reduced))


def main():
    stats = {"run": 0, "passed": 0}
    failures = []

    # 1. Exhaustive over all graphs with n <= 5 and a range of k values.
    max_n = 5
    for n in range(0, max_n + 1):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                check(instance, solve_clique(instance), stats, failures)

    # 2. Randomized larger instances.
    random.seed(20240607)
    for _ in range(3000):
        n = random.randint(0, 8)
        allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edges = [list(e) for e in allp if random.random() < 0.5]
        k = random.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        check(instance, solve_clique(instance), stats, failures)

    # 3. Explicit edge cases from the problem statement.
    edge_cases = [
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": -5}, True),
        ({"n": 0, "edges": [], "k": 1}, False),
        ({"n": 0, "edges": [], "k": 3}, False),
        ({"n": 1, "edges": [], "k": 1}, True),
        ({"n": 1, "edges": [], "k": 2}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}, False),
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 4}, True),
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 3}, False),
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2]], "k": 3}, True),
    ]
    for instance, expected in edge_cases:
        check(instance, expected, stats, failures)

    print(f"tests_run={stats['run']} tests_passed={stats['passed']}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print("  instance=", f[0], "expected=", f[1], "got=", f[2])
        sys.exit(1)
    print("ALL TESTS PASSED")

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": stats["run"] == stats["passed"],
                "tests_run": stats["run"],
                "tests_passed": stats["passed"],
            },
            fh,
        )


if __name__ == "__main__":
    main()

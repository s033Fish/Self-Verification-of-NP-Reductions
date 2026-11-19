"""Tests for the 3-Coloring -> 3-SAT reduction in reduce.py.

problems.py provides no solvers, so solvers for both problems are defined
here from the problem definitions.  Small instances are solved by plain
brute force; a simple backtracking / unit-propagation solver is used for
larger instances and cross-checked against brute force on small ones.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers

def brute_three_coloring(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def brute_three_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for values in itertools.product([False, True], repeat=m):
        if all(
            any((lit > 0) == values[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Backtracking solvers (complete, used for larger instances)

def backtrack_three_coloring(instance) -> bool:
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def rec(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            if all(colour[w] != c for w in adj[v]):
                colour[v] = c
                if rec(v + 1):
                    return True
                colour[v] = -1
        return False

    return rec(0)


def backtrack_three_sat(instance) -> bool:
    """Simple DPLL with unit propagation on a 3-CNF formula."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assign):
        # assign: dict var -> bool; returns simplified clauses or None if
        # a clause became empty (conflict).
        out = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assign:
                    if (lit > 0) == assign[var]:
                        satisfied = True
                        break
                else:
                    new_clause.append(lit)
            if not satisfied:
                if not new_clause:
                    return None
                out.append(new_clause)
        return out

    def dpll(clauses, assign):
        # Unit propagation.
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                if len(clause) == 1:
                    lit = clause[0]
                    var = abs(lit)
                    val = lit > 0
                    if var in assign:
                        if assign[var] != val:
                            return False
                    else:
                        assign = dict(assign)
                        assign[var] = val
                        clauses = simplify(clauses, assign)
                        if clauses is None:
                            return False
                        changed = True
                        break
        if not clauses:
            return True
        # Choose a variable from the first clause.
        var = abs(clauses[0][0])
        for val in (True, False):
            new_assign = dict(assign)
            new_assign[var] = val
            new_clauses = simplify(clauses, new_assign)
            if new_clauses is not None and dpll(new_clauses, new_assign):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n, max_edges=None):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(pairs) + 1):
        if max_edges is not None and r > max_edges:
            break
        for combo in itertools.combinations(pairs, r):
            yield {"n": n, "edges": [list(e) for e in combo]}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(condition, message):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            print("FAIL:", message)

    # 0. Cross-check the backtracking solvers against brute force on all
    #    graphs with up to 4 vertices.
    for n in range(0, 5):
        for graph in all_graphs(n):
            expected = brute_three_coloring(graph)
            check(
                expected == backtrack_three_coloring(graph),
                f"coloring solver disagreement n={n} edges={graph['edges']}",
            )
            out = reduce(graph)
            check(
                brute_three_sat(out) == backtrack_three_sat(out),
                f"sat solver disagreement n={n} edges={graph['edges']}",
            )

    # 1. Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for graph in all_graphs(n):
            SOURCE.validate(graph)
            out = reduce(graph)
            TARGET.validate(out)
            expected = backtrack_three_coloring(graph)
            got = backtrack_three_sat(out)
            check(
                expected == got,
                f"mismatch n={n} edges={graph['edges']}: "
                f"coloring={expected} sat={got}",
            )

    # 2. Random graphs, including dense ones (K4, K5, ...).
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
        graph = random_graph(n, p, rng)
        SOURCE.validate(graph)
        out = reduce(graph)
        TARGET.validate(out)
        check(
            backtrack_three_coloring(graph) == backtrack_three_sat(out),
            f"mismatch random n={n} p={p} edges={graph['edges']}",
        )

    # 3. Specific edge cases.
    # n = 0 is yes.
    check(brute_three_coloring({"n": 0, "edges": []}), "n=0 should be yes")
    check(
        backtrack_three_sat(reduce({"n": 0, "edges": []})),
        "reduction of n=0 should be yes",
    )
    # K4 is no.
    k4 = {"n": 4, "edges": [[u, v] for u in range(4) for v in range(u + 1, 4)]}
    check(not backtrack_three_coloring(k4), "K4 should be no")
    check(not backtrack_three_sat(reduce(k4)), "reduction of K4 should be no")
    # K3 is yes.
    k3 = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}
    check(backtrack_three_coloring(k3), "K3 should be yes")
    check(backtrack_three_sat(reduce(k3)), "reduction of K3 should be yes")
    # Any graph with at most 3 vertices is yes.
    for n in range(0, 4):
        for graph in all_graphs(n):
            check(
                backtrack_three_coloring(graph),
                f"graph with {n} vertices should be yes: {graph['edges']}",
            )

    # 4. Structure checks on the produced instance.
    graph = {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}
    out = reduce(graph)
    check(out["num_vars"] == 3 * 5 + 1, "num_vars should be 3n+1")
    check(
        all(len(c) == 3 for c in out["clauses"]),
        "every clause must have 3 literals",
    )
    check(
        all(len({abs(l) for l in c}) == 3 for c in out["clauses"]),
        "every clause must use 3 different variables",
    )
    check(
        all(l != 0 and abs(l) <= out["num_vars"] for c in out["clauses"] for l in c),
        "all literals in range",
    )
    # Clause count: n + 6n + 6|E| = 7n + 6|E|.
    check(
        len(out["clauses"]) == 7 * 5 + 6 * len(graph["edges"]),
        "unexpected clause count",
    )

    # 5. Empty formula / no clauses is satisfiable for any m.
    check(brute_three_sat({"num_vars": 0, "clauses": []}), "empty formula m=0")
    check(brute_three_sat({"num_vars": 7, "clauses": []}), "empty formula m=7")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

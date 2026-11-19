"""Tests for the Dominating Set -> SAT reduction in reduce.py.

Includes independent solvers for both problems, written from the definitions
in problems.py, and compares them on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Independent brute-force solver for Dominating Set

def brute_dominating_set(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            D = set(combo)
            if all(u in D or (adj[u] & D) for u in range(n)):
                return True
    return False


# ----------------------------------------------------------------------
# Independent SAT solver: DPLL (complete, correct)

def _dpll(clauses, assignment):
    # clauses: list of tuples of literals; assignment: dict var->bool
    def lit_val(l):
        v = abs(l)
        if v not in assignment:
            return None
        return assignment[v] if l > 0 else not assignment[v]

    # Simplify
    simplified = []
    for clause in clauses:
        new_clause = []
        satisfied = False
        for l in clause:
            val = lit_val(l)
            if val is True:
                satisfied = True
                break
            if val is None:
                new_clause.append(l)
        if satisfied:
            continue
        if not new_clause:
            return False  # empty clause -> conflict
        simplified.append(tuple(new_clause))

    if not simplified:
        return True  # all clauses satisfied

    # Unit propagation
    units = [c[0] for c in simplified if len(c) == 1]
    if units:
        assignment = dict(assignment)
        for l in units:
            v = abs(l)
            val = l > 0
            if v in assignment and assignment[v] != val:
                return False
            assignment[v] = val
        return _dpll(simplified, assignment)

    # Choose a variable (most frequent)
    counts = {}
    for c in simplified:
        for l in c:
            counts[abs(l)] = counts.get(abs(l), 0) + 1
    var = max(counts, key=counts.get)

    for val in (True, False):
        new_assign = dict(assignment)
        new_assign[var] = val
        if _dpll(simplified, new_assign):
            return True
    return False


def solve_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]
    if m <= 12:
        # cross-check with exhaustive brute force on tiny formulas
        return brute_sat(instance)
    return _dpll(clauses, {})


def brute_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def random_graph(rng, n, p):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def check(instance, label):
    DominatingSet.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = brute_dominating_set(instance)
    got = solve_sat(out)
    assert got == expected, (
        f"MISMATCH [{label}]: instance={instance} expected={expected} got={got} "
        f"reduced={out}"
    )
    return expected


# ----------------------------------------------------------------------
# Tests

def test_edge_cases():
    cases = [
        ({"n": 0, "edges": [], "k": 0}, "empty graph k=0"),
        ({"n": 0, "edges": [], "k": 5}, "empty graph k=5"),
        ({"n": 0, "edges": [], "k": -1}, "empty graph k=-1"),
        ({"n": 1, "edges": [], "k": 0}, "single isolated k=0"),
        ({"n": 1, "edges": [], "k": 1}, "single isolated k=1"),
        ({"n": 1, "edges": [], "k": -3}, "single isolated k<0"),
        ({"n": 3, "edges": [], "k": 2}, "3 isolated k=2 (no)"),
        ({"n": 3, "edges": [], "k": 3}, "3 isolated k=3 (yes)"),
        ({"n": 3, "edges": [], "k": 10}, "3 isolated k=10 (yes)"),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, "two disjoint edges k=2"),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, "two disjoint edges k=1"),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2}, "path5 k=2"),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1}, "path5 k=1"),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 0], [2, 3]], "k": 1}, "triangle+tail k=1"),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 0], [2, 3]], "k": 2}, "triangle+tail k=2"),
        ({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3}, "3 disjoint edges k=3"),
        ({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2}, "3 disjoint edges k=2"),
        ({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 2}, "C6 k=2"),
        ({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 1}, "C6 k=1"),
    ]
    count = 0
    for inst, label in cases:
        check(inst, label)
        count += 1
    return count


def test_random():
    rng = random.Random(12345)
    count = 0
    for n in range(0, 9):
        for _ in range(40):
            p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
            edges = random_graph(rng, n, p)
            k = rng.randint(-2, n + 2)
            check({"n": n, "edges": edges, "k": k}, f"random n={n} p={p} k={k}")
            count += 1
    return count


def test_exhaustive_small():
    """Exhaustively test all graphs on up to 4 vertices, all k."""
    count = 0
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k},
                      f"exhaustive n={n} mask={mask} k={k}")
                count += 1
    return count


def test_larger():
    """Larger graphs where brute force is still feasible (k small)."""
    rng = random.Random(999)
    count = 0
    for n in range(9, 14):
        for _ in range(15):
            edges = random_graph(rng, n, 0.25)
            for k in range(0, 4):
                check({"n": n, "edges": edges, "k": k}, f"larger n={n} k={k}")
                count += 1
    return count


def main():
    total = 0
    total += test_edge_cases()
    total += test_random()
    total += test_exhaustive_small()
    total += test_larger()
    print(f"ALL TESTS PASSED: {total} instances checked")
    return total


if __name__ == "__main__":
    main()

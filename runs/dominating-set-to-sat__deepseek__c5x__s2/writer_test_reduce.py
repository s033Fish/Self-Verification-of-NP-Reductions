"""Brute-force solvers for both problems plus tests of the reduction."""

from __future__ import annotations

import itertools
import random

from problems import DominatingSet, Sat
from reduce import reduce


# ---------------------------------------------------------------- solvers
def solve_dominating_set(instance: dict) -> bool:
    """Brute force: try every subset of vertices of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    for size in range(0, k + 1):
        for chosen in itertools.combinations(range(n), size):
            covered = set(chosen)
            for c in chosen:
                covered |= adj[c]
            if len(covered) == n:
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Exact DPLL SAT solver with unit propagation."""
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, var, val):
        """Assign var=val, simplify.  Return None if unsatisfiable."""
        new = []
        for clause in clauses:
            if (var if val else -var) in clause:
                continue  # clause satisfied
            rest = [lit for lit in clause if lit != (-var if val else var)]
            if not rest:
                return None  # empty clause -> conflict
            new.append(rest)
        return new

    def unit_propagate(clauses):
        while True:
            if any(len(c) == 0 for c in clauses):
                return None
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                return clauses
            clauses = simplify(clauses, abs(unit), unit > 0)
            if clauses is None:
                return None

    def dpll(clauses):
        clauses = unit_propagate(clauses)
        if clauses is None:
            return False
        if not clauses:
            return True
        var = abs(min(clauses, key=len)[0])
        for val in (True, False):
            sub = simplify(clauses, var, val)
            if sub is not None and dpll(sub):
                return True
        return False

    return dpll(clauses)


# ---------------------------------------------------------------- tests
def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance):
    DominatingSet.validate(instance)
    expected = solve_dominating_set(instance)
    target = reduce(instance)
    Sat.validate(target)
    got = solve_sat(target)
    assert expected == got, (instance, target, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance)
            tests_passed += 1
        except AssertionError as exc:
            failures.append(exc)

    # Exhaustive: every graph on 0..4 vertices, every k in -2..n+2.
    for n in range(0, 5):
        for graph in all_graphs(n):
            for k in range(-2, n + 3):
                run({"n": graph["n"], "edges": graph["edges"], "k": k})

    # Random graphs on up to 9 vertices with random k.
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 9)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.35:
                    edges.append([u, v])
        k = rng.randint(-1, n + 1)
        run({"n": n, "edges": edges, "k": k})

    # A few structured edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": 5})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 5, "edges": [], "k": 4})   # isolated vertices
    run({"n": 5, "edges": [], "k": 5})
    run({"n": 6, "edges": [[i, i + 1] for i in range(5)], "k": 2})
    run({"n": 6, "edges": [[i, i + 1] for i in range(5)], "k": 1})
    # Complete graphs
    for n in range(1, 8):
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for k in range(-1, n + 2):
            run({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:5]:
            print(f)
        raise SystemExit(1)

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    print("verdict.json written")


if __name__ == "__main__":
    main()

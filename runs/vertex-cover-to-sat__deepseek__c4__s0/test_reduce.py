"""Tests for the Vertex Cover -> SAT reduction in reduce.py.

Includes independent brute-force / DPLL solvers for both problems and
compares their answers on many small source instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written directly from the problem definitions.

def solve_vertex_cover(instance: dict) -> bool:
    """Brute force over subsets of vertices (small n only)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """DPLL-style complete SAT solver (handles auxiliary variables)."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, lit):
        """Assign lit true; return simplified clause list or None if unsat."""
        new = []
        for clause in clauses:
            if lit in clause:
                continue
            reduced = [l for l in clause if l != -lit]
            if not reduced:
                return None
            new.append(reduced)
        return new

    def dpll(clauses):
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        # unit propagation
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        # pure literal elimination (optional, helps)
        # pick a literal from the shortest clause
        shortest = min(clauses, key=len)
        lit = shortest[0]
        for choice in (lit, -lit):
            sub = simplify(clauses, choice)
            if sub is not None and dpll(sub):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generators.

def random_vertex_cover(rng: random.Random, max_n: int = 6) -> dict:
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(possible)
    num_edges = rng.randint(0, len(possible))
    edges = [list(e) for e in possible[:num_edges]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def all_vertex_covers_up_to(n: int):
    """Exhaustive small instances: all graphs on n vertices, all k."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        for k in range(-1, n + 2):
            yield {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = solve_vertex_cover(instance)
        got = solve_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    # Exhaustive small cases.
    for n in range(0, 5):
        for instance in all_vertex_covers_up_to(n):
            check(instance)

    # Random larger cases.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_vertex_cover(rng, max_n=7))

    # Hand-picked edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": -3},
        {"n": 5, "edges": [[0, 1]], "k": 0},
        {"n": 5, "edges": [[0, 1]], "k": 1},
        {"n": 5, "edges": [[0, 1]], "k": 5},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 4},
        {"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 5},
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:5]:
            print("  instance:", f[0])
            print("  reduced :", f[1])
            print("  expected:", f[2], "got:", f[3])
        raise SystemExit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()

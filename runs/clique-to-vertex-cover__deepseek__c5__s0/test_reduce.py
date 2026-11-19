"""Independent brute-force verification of reduce.py (Clique -> Vertex Cover).

We implement brute-force solvers for both problems directly from the
docstring definitions, generate many small source instances (including the
documented edge cases), reduce each with reduce.reduce, and compare answers.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions only)

def clique_yes(instance: dict) -> bool:
    """Yes iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def vertex_cover_yes(instance: dict) -> bool:
    """Yes iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_instance(rng: random.Random, n: int, p: float, k: int) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges, "k": k}


def all_instances():
    """Exhaustive over all graphs on n<=4 with a range of k, plus randoms."""
    insts = []
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
            for k in range(-2, n + 3):
                insts.append({"n": n, "edges": edges, "k": k})
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
        k = rng.randint(-3, n + 3)
        insts.append(random_instance(rng, n, p, k))
    return insts


def main() -> None:
    insts = all_instances()
    tests_run = 0
    tests_passed = 0
    failures = []
    for inst in insts:
        # Both problems accept the same instance format; validate.
        Clique.validate(inst)
        expected = clique_yes(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        got = vertex_cover_yes(reduced)
        tests_run += 1
        if got == expected:
            tests_passed += 1
        elif len(failures) < 20:
            failures.append((inst, reduced, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, reduced, expected, got in failures:
            print(f"  src={inst} reduced={reduced} expected={expected} got={got}")
    else:
        print("ALL PASSED")


if __name__ == "__main__":
    main()

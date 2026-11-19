"""Tests for the Clique -> Vertex Cover reduction.

Includes brute-force solvers written from the problem definitions, then
compares solver answers on many small source instances against the answers
of their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions

def clique_solver(instance: dict) -> bool:
    """Yes iff the graph has a clique of at least k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(combo, 2)):
                return True
    return False


def vertex_cover_solver(instance: dict) -> bool:
    """Yes iff the graph has a vertex cover of at most k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_graph(rng: random.Random, n: int, p: float) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def generate_instances():
    instances = []

    # Exhaustive small graphs with every relevant k.
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.2, 0.5, 0.8, 1.0])
        edges = random_graph(rng, n, p)
        k = rng.randint(-3, n + 3)
        instances.append({"n": n, "edges": edges, "k": k})

    # Complete and empty graphs explicitly.
    for n in range(0, 8):
        complete = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for k in range(-2, n + 3):
            instances.append({"n": n, "edges": list(complete), "k": k})
            instances.append({"n": n, "edges": [], "k": k})

    return instances


def main() -> None:
    instances = generate_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for instance in instances:
        # Both problems must accept the instance.
        Clique.validate(instance)
        reduced = reduce(instance)
        VertexCover.validate(reduced)

        source_answer = clique_solver(instance)
        reduced_answer = vertex_cover_solver(reduced)

        tests_run += 1
        if source_answer == reduced_answer:
            tests_passed += 1
        else:
            failures.append((instance, reduced, source_answer, reduced_answer))

    # Also check the reduction does not mutate its input.
    probe = {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2}
    snapshot = {"n": probe["n"], "edges": [list(e) for e in probe["edges"]], "k": probe["k"]}
    reduce(probe)
    tests_run += 1
    if probe == snapshot:
        tests_passed += 1
    else:
        failures.append(("mutation", probe, snapshot, None))

    # Idempotence / determinism check.
    for instance in instances[:50]:
        tests_run += 1
        if reduce(instance) == reduce(instance):
            tests_passed += 1
        else:
            failures.append(("nondeterministic", instance, None, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for failure in failures[:10]:
            print(failure)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

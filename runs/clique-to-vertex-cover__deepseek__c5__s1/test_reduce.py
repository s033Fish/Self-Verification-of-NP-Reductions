"""Independent tests for reduce.py (Clique -> Vertex Cover).

We write our own brute-force solvers from the problem definitions and
compare, on many small instances, the source answer with the target answer
of the reduction.  We also validate that reduce() returns well-formed
instances and runs in polynomial time.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import Clique, VertexCover, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the definitions.
# ----------------------------------------------------------------------

def has_edge(edges, u, v):
    return any((a == u and b == v) or (a == v and b == u) for a, b in edges)


def clique_solver(instance) -> bool:
    """Yes iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(has_edge(edges, u, v)
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def vertex_cover_solver(instance) -> bool:
    """Yes iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
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
# ----------------------------------------------------------------------

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def all_graphs(n):
    """Every simple graph on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Clique.validate(instance)
        except InvalidInstance as exc:
            failures.append(f"{label}: invalid source instance: {exc}")
            return
        expected = clique_solver(instance)
        try:
            reduced = reduce(instance)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: reduce raised {exc!r}")
            return
        # Target must be a valid instance.
        try:
            VertexCover.validate(reduced)
        except InvalidInstance as exc:
            failures.append(f"{label}: invalid target instance: {exc}")
            return
        # Reduction must preserve n and edges must be a simple graph.
        if reduced["n"] != instance["n"]:
            failures.append(f"{label}: n changed")
            return
        got = vertex_cover_solver(reduced)
        if got != expected:
            failures.append(
                f"{label}: source={expected} target={got} "
                f"instance={instance} reduced={reduced}"
            )
            return
        tests_passed += 1

    # 1. Exhaustive over all graphs for n = 0..5 and all relevant k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k},
                      f"exhaustive n={n} k={k} edges={edges}")

    # 2. Random graphs for n = 6..9 with random k.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(6, 9)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k},
              f"random n={n} p={p} k={k}")

    # 3. Specific edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 3},
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 4},
    ]
    for inst in edge_cases:
        check(inst, f"edge-case {inst}")

    # 4. Polynomial-time sanity: reduction on a large instance should be fast.
    n_big = 300
    edges_big = random_graph(n_big, 0.5, rng)
    start = time.time()
    reduce({"n": n_big, "edges": edges_big, "k": n_big // 2})
    elapsed = time.time() - start
    tests_run += 1
    if elapsed > 5.0:
        failures.append(f"reduce too slow on n={n_big}: {elapsed:.2f}s")
    else:
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
        print(f"total failures: {len(failures)}")
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()

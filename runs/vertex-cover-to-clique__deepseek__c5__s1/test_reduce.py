"""Independent verification of reduce.py (Vertex Cover -> Clique).

We implement brute-force solvers directly from the problem definitions,
generate many small source instances (including edge cases), reduce them,
and check that the source and target answers agree.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the docstrings.

def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # Empty set covers a graph with no edges; k >= 0 handled above.
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def solve_clique(instance: dict) -> bool:
    """Yes iff there is a clique of size AT LEAST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = {u: set() for u in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if b not in adj[a]:
                    ok = False
                    break
            if ok:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def make_instance(n, edges, k):
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask & (1 << i)]
        yield edges


def generate_source_instances():
    instances = []
    # Exhaustive over all graphs for n = 0..4, all k in a wide range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instances.append(make_instance(n, edges, k))
    # Random larger graphs (n up to 7) with random k.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 7)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        instances.append(make_instance(n, edges, k))
    return instances


def main():
    instances = generate_source_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        # Inputs must be valid source instances.
        SOURCE.validate(inst)
        reduced = reduce(inst)
        # The reduction must produce a valid target instance.
        TARGET.validate(reduced)

        expected = solve_vertex_cover(inst)
        got = solve_clique(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, reduced, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (showing up to 10):")
        for inst, reduced, expected, got in failures[:10]:
            print(f"  source={inst} -> target={reduced} "
                  f"expected={expected} got={got}")
    else:
        print("All reductions preserved the answer.")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()

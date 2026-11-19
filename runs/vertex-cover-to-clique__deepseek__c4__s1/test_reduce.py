"""Tests for the Vertex Cover -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def vertex_cover_answer(instance):
    """True iff graph has a vertex cover of at most k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def clique_answer(instance):
    """True iff graph has a clique of at least k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    if k == 1:
        return n >= 1
    adj = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if (a, b) not in adj:
                    ok = False
                    break
            if ok:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def random_source_instance(rng):
    n = rng.randint(0, 7)
    p = rng.choice([0.0, 0.2, 0.5, 0.8, 1.0])
    edges = random_graph(n, p, rng)
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    instances = []

    # Exhaustive-ish small instances: all graphs on n <= 4, all k.
    for n in range(0, 5):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    for _ in range(3000):
        instances.append(random_source_instance(rng))

    for inst in instances:
        VertexCover.validate(inst)
        expected = vertex_cover_answer(inst)
        red = reduce(inst)
        Clique.validate(red)
        got = clique_answer(red)
        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            print("FAIL", inst, "expected", expected, "reduced", red, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()

"""Tests for the Vertex Cover -> Clique reduction."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def vertex_cover_yes(instance) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def clique_yes(instance) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = {(u, v) for u, v in edges}
    adj |= {(v, u) for u, v in edges}
    for subset in itertools.combinations(range(n), k):
        if all((u, v) in adj for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = []

    # Hand-picked edge cases.
    instances.append({"n": 0, "edges": [], "k": 0})
    instances.append({"n": 0, "edges": [], "k": -1})
    instances.append({"n": 0, "edges": [], "k": 1})
    instances.append({"n": 1, "edges": [], "k": 0})
    instances.append({"n": 1, "edges": [], "k": 1})
    instances.append({"n": 1, "edges": [], "k": -1})
    instances.append({"n": 3, "edges": [], "k": 0})
    instances.append({"n": 3, "edges": [], "k": -5})
    instances.append({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    instances.append({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    instances.append({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    instances.append({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    instances.append({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})
    instances.append({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1})
    instances.append({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0})

    # Random instances.
    for _ in range(600):
        instances.append(random_instance(rng))

    for inst in instances:
        tests_run += 1
        problems.VertexCover.validate(inst)
        reduced = reduce(inst)
        problems.Clique.validate(reduced)
        src = vertex_cover_yes(inst)
        tgt = clique_yes(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, reduced, src, tgt))

    if failures:
        print("FAILURES:")
        for inst, reduced, src, tgt in failures[:20]:
            print(f"  {inst} -> {reduced}: source={src}, target={tgt}")
    print(f"tests_run={tests_run}, tests_passed={tests_passed}")
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

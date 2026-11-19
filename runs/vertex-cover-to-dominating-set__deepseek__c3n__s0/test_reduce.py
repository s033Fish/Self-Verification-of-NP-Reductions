"""Brute-force solvers and randomized tests for the VC -> DS reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def vertex_cover_yes(instance) -> bool:
    """True iff the graph has a vertex cover of size at most k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_yes(instance) -> bool:
    """True iff the graph has a dominating set of size at most k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness.

def random_instance(rng: random.Random, max_n: int = 7) -> dict:
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    rng.shuffle(edges)
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    # 1) Randomized cross-checks.
    for _ in range(4000):
        inst = random_instance(rng)
        SOURCE.validate(inst)
        red = reduce(inst)
        TARGET.validate(red)
        src = vertex_cover_yes(inst)
        tgt = dominating_set_yes(red)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    # 2) Hand-picked edge cases.
    hand_cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 0},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 0], [3, 4]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 0], [3, 4]], "k": 2},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 0},
    ]
    for inst in hand_cases:
        SOURCE.validate(inst)
        red = reduce(inst)
        TARGET.validate(red)
        src = vertex_cover_yes(inst)
        tgt = dominating_set_yes(red)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    # 3) Exhaustive over all graphs on up to 4 vertices and a range of k.
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if mask >> i & 1]
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": edges, "k": k}
                SOURCE.validate(inst)
                red = reduce(inst)
                TARGET.validate(red)
                src = vertex_cover_yes(inst)
                tgt = dominating_set_yes(red)
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((inst, red, src, tgt))

    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        raise SystemExit(1)

    print(f"All tests passed: {tests_passed}/{tests_run}")


if __name__ == "__main__":
    main()

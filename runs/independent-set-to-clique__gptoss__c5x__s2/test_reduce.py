"""Independent verification of reduce.py (Independent Set -> Clique).

We implement our own brute-force solvers directly from the problem
definitions in problems.py (which provides only validate()), then compare
solver answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def _adjacency(n, edges):
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    return adj


def max_independent_set_size(n, edges):
    """Largest set of vertices with no edge between any two of them."""
    adj = _adjacency(n, edges)
    best = 0
    for size in range(n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if adj[a][b]:
                    ok = False
                    break
            if ok:
                best = size
                break  # a set of this size exists; try larger
    return best


def max_clique_size(n, edges):
    """Largest set of vertices with an edge between every two of them."""
    adj = _adjacency(n, edges)
    best = 0
    for size in range(n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                best = size
                break
    return best


def solve_independent_set(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_independent_set_size(n, edges) >= k


def solve_clique(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_clique_size(n, edges) >= k


# ----------------------------------------------------------------------
# Instance generation (all small graphs, plus random ones).
# ----------------------------------------------------------------------

def all_graphs(n):
    """Every simple graph on n labelled vertices, as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def random_graph(n, rng, p=0.5):
    return [
        [u, v]
        for u, v in itertools.combinations(range(n), 2)
        if rng.random() < p
    ]


def check(instance, label, failures):
    """Compare source answer, reduced answer, and validity."""
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)  # must be a well-formed target instance
    src = solve_independent_set(instance)
    tgt = solve_clique(reduced)
    if src != tgt:
        failures.append((label, instance, reduced, src, tgt))
    return src == tgt


def main():
    failures = []
    tests_run = 0

    # 1. Exhaustive over all graphs for n = 0..4 and all k in a wide range.
    for n in range(0, 5):
        ks = list(range(-2, n + 3))
        for edges in all_graphs(n):
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                tests_run += 1
                check(instance, f"exhaustive n={n} k={k}", failures)

    # 2. Random graphs, n up to 8, random k (including negatives and > n).
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng, rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]))
        k = rng.randint(-3, n + 3)
        instance = {"n": n, "edges": edges, "k": k}
        tests_run += 1
        check(instance, f"random n={n} k={k}", failures)

    # 3. Targeted edge cases.
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 5},          # no edges -> IS yes
        {"n": 5, "edges": [], "k": 6},          # k > n -> no
        {"n": 5, "edges": [], "k": 0},          # k <= 0 -> yes
        {"n": 5, "edges": [], "k": -1},         # k <= 0 -> yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
    ]
    for instance in targeted:
        tests_run += 1
        check(instance, "targeted", failures)

    # 4. Confirm the reduction really is the complement (structural check).
    for _ in range(200):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng)
        inst = {"n": n, "edges": edges, "k": 1}
        red = reduce(inst)
        orig = {frozenset(e) for e in edges}
        comp = {frozenset(e) for e in red["edges"]}
        allpairs = {frozenset(p) for p in itertools.combinations(range(n), 2)}
        assert red["n"] == n and red["k"] == 1
        assert comp == allpairs - orig, "not the complement graph"
        assert len(red["edges"]) == len(comp), "duplicate edges produced"
        tests_run += 1

    tests_passed = tests_run - len(failures)
    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for label, inst, red, src, tgt in failures[:10]:
        print("FAIL", label, inst, "->", red, "src=", src, "tgt=", tgt)

    import json
    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": len(failures) == 0, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )
    print("verdict.json written")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

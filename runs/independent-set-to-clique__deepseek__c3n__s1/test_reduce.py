"""Tests for the Independent Set -> Clique reduction.

Includes brute-force solvers for both problems (from the definitions in
problems.py) and compares answers on many small random instances.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce


def _adjacency(instance):
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def brute_independent_set(instance):
    """Yes iff there is an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(v not in adj[u] for u, v in itertools.combinations(combo, 2)):
                return True
    return False


def brute_clique(instance):
    """Yes iff there is a clique of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(v in adj[u] for u, v in itertools.combinations(combo, 2)):
                return True
    return False


def random_instance(rng, max_n=7):
    n = rng.randint(0, max_n)
    all_edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = all_edges[:m]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Deterministic edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 4},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 5},
    ]

    instances = list(edge_cases)
    for _ in range(3000):
        instances.append(random_instance(rng))

    for inst in instances:
        # Both validators must accept the source instance.
        IndependentSet.validate(inst)
        reduced = reduce(inst)
        # The reduction must produce a valid Clique instance.
        Clique.validate(reduced)

        expected = brute_independent_set(inst)
        got = brute_clique(reduced)

        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", reduced, "expected", expected, "got", got)

    # Also verify the reduction is a genuine complement: independent set in
    # source is a clique in target for every subset, exhaustively on small n.
    for n in range(0, 6):
        all_edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [all_edges[i] for i in range(len(all_edges)) if mask >> i & 1]
            inst = {"n": n, "edges": edges, "k": 0}
            reduced = reduce(inst)
            src_adj = _adjacency(inst)
            tgt_adj = _adjacency(reduced)
            for size in range(n + 1):
                for combo in itertools.combinations(range(n), size):
                    indep = all(v not in src_adj[u] for u, v in itertools.combinations(combo, 2))
                    clique = all(v in tgt_adj[u] for u, v in itertools.combinations(combo, 2))
                    tests_run += 1
                    if indep == clique:
                        tests_passed += 1
                    else:
                        print("FAIL subset", n, edges, combo, indep, clique)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()

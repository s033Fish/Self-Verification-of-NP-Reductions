"""Brute-force solvers and randomized tests for the Clique -> IS reduction."""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance):
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


def brute_independent_set(instance):
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
            if not any(adj[a][b] for a, b in itertools.combinations(combo, 2)):
                return True
    return False


def random_instance(rng):
    n = rng.randint(0, 7)
    all_edges = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    for _ in range(3000):
        inst = random_instance(rng)
        Clique.validate(inst)
        out = reduce(inst)
        IndependentSet.validate(out)
        expected = brute_clique(inst)
        got = brute_independent_set(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", out, "expected", expected, "got", got)
            break
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json

    with open("verdict.json", "w") as f:
        json.dump(
            {
                "verified": tests_run == tests_passed,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            f,
        )


if __name__ == "__main__":
    main()

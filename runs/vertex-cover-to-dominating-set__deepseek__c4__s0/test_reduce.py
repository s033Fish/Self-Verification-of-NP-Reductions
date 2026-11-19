"""Tests for reduce.py: brute-force solvers + randomized comparison."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


def brute_vertex_cover(instance) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
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


def brute_dominating_set(instance) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
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
            if all(v in chosen or (adj[v] & chosen) for v in range(n)):
                return True
    return False


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive over all small graphs and all relevant k.
    for n in range(0, 5):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                SOURCE.validate(inst)
                src = brute_vertex_cover(inst)
                red = reduce(inst)
                TARGET.validate(red)
                tgt = brute_dominating_set(red)
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    print("FAIL", inst, "->", red, src, tgt)
                    return tests_run, tests_passed

    # 2. Random small graphs (kept small so brute force stays cheap).
    for _ in range(3000):
        n = rng.randint(0, 5)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.75, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-1, 3)
        inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
        SOURCE.validate(inst)
        src = brute_vertex_cover(inst)
        red = reduce(inst)
        TARGET.validate(red)
        tgt = brute_dominating_set(red)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", red, src, tgt)
            return tests_run, tests_passed

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")

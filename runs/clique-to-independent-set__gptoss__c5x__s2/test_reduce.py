"""Independent verification of reduce.py (Clique -> Independent Set).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, Any, List

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the docstrings only.

def _adjacency(instance: Dict[str, Any]):
    n = instance["n"]
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    return n, adj


def clique_has_at_least_k(instance: Dict[str, Any]) -> bool:
    """True iff graph has a clique of size >= k."""
    Clique.validate(instance)
    n, adj = _adjacency(instance)
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def independent_set_has_at_least_k(instance: Dict[str, Any]) -> bool:
    """True iff graph has an independent set of size >= k."""
    IndependentSet.validate(instance)
    n, adj = _adjacency(instance)
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


# ----------------------------------------------------------------------
# Instance helpers

def make_instance(n, edges, k):
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def all_graphs(n):
    """All simple undirected graphs on n labelled vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def random_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return make_instance(n, edges, k)


# ----------------------------------------------------------------------
# Tests

tests_run = 0
tests_passed = 0
failures: List[str] = []


def check(cond: bool, msg: str):
    global tests_run, tests_passed
    tests_run += 1
    if cond:
        tests_passed += 1
    else:
        failures.append(msg)


def main():
    rng = random.Random(12345)

    # 1. Exhaustive: all graphs on n = 0..4, all k from -2 to n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = make_instance(n, edges, k)
                tgt = reduce(src)
                # reduce must produce a valid target instance
                IndependentSet.validate(tgt)
                a = clique_has_at_least_k(src)
                b = independent_set_has_at_least_k(tgt)
                check(
                    a == b,
                    f"exhaustive mismatch n={n} edges={edges} k={k}: "
                    f"clique={a} indep={b} target={tgt}",
                )

    # 2. Random larger instances.
    for _ in range(3000):
        src = random_instance(rng, max_n=7)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = clique_has_at_least_k(src)
        b = independent_set_has_at_least_k(tgt)
        check(
            a == b,
            f"random mismatch src={src}: clique={a} indep={b} target={tgt}",
        )

    # 3. Specific edge cases.
    edge_cases = [
        make_instance(0, [], 0),
        make_instance(0, [], 1),
        make_instance(0, [], -5),
        make_instance(1, [], 1),
        make_instance(1, [], 2),
        make_instance(1, [], 0),
        make_instance(5, [], 5),          # no edges: clique only k<=1
        make_instance(5, [], 0),
        make_instance(5, [], 6),
        make_instance(5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]], 3),
        make_instance(4, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], 4),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 3),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 4),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], -1),
    ]
    for src in edge_cases:
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = clique_has_at_least_k(src)
        b = independent_set_has_at_least_k(tgt)
        check(a == b, f"edge-case mismatch src={src}: clique={a} indep={b} target={tgt}")

    # 4. reduce must not mutate the input.
    src = make_instance(4, [[0, 1], [2, 3]], 2)
    snapshot = {"n": src["n"], "edges": [list(e) for e in src["edges"]], "k": src["k"]}
    reduce(src)
    check(src == snapshot, f"reduce mutated its input: {src} != {snapshot}")

    # 5. Complement structure sanity: target edges are exactly non-edges of src.
    for _ in range(200):
        src = random_instance(rng, max_n=7)
        tgt = reduce(src)
        n = src["n"]
        orig = {frozenset(e) for e in src["edges"]}
        comp = {frozenset(e) for e in tgt["edges"]}
        all_pairs = {frozenset(p) for p in itertools.combinations(range(n), 2)}
        check(comp == all_pairs - orig, f"complement wrong for src={src}: {tgt}")
        check(tgt["n"] == n and tgt["k"] == src["k"],
              f"n/k not preserved for src={src}: {tgt}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

"""Independent brute-force checks of reduce.py for VertexCover -> DominatingSet.

We implement our own solvers straight from the problem docstrings and compare
the source answer with the answer to the reduced target instance over many
small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import VertexCover, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py.

def _min_vertex_cover(n, edges):
    """Minimum size of a vertex cover (exhaustive)."""
    best = None
    for r in range(n + 1):
        for comb in itertools.combinations(range(n), r):
            chosen = set(comb)
            if all(u in chosen or v in chosen for u, v in edges):
                return r  # smallest r first
    return n  # unreachable for r == n


def vc_solver(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return _min_vertex_cover(n, edges) <= k


def _min_dominating_set(n, edges):
    """Minimum size of a dominating set (exhaustive)."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for r in range(n + 1):
        for comb in itertools.combinations(range(n), r):
            chosen = set(comb)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return r
    return n


def ds_solver(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return _min_dominating_set(n, edges) <= k


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    try:
        VertexCover.validate(instance)
        src = vc_solver(instance)
        red = reduce(instance)
        DominatingSet.validate(red)
        tgt = ds_solver(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, instance, red, src, tgt))
    except Exception as exc:  # noqa: BLE001
        failures.append((label, instance, None, "EXC", repr(exc)))


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def main():
    random.seed(12345)

    # 1) Exhaustive over all graphs with n = 0..5 and a wide range of k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [e[:] for e in edges], "k": k},
                      f"exhaustive n={n} k={k}")

    # 2) Random larger instances.
    for trial in range(3000):
        n = random.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        random.shuffle(pairs)
        m = random.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        k = random.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, f"random trial={trial}")

    # 3) Targeted edge cases.
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 4, "edges": [[0, 1]], "k": 0},
        {"n": 4, "edges": [[0, 1]], "k": 1},
        {"n": 4, "edges": [[0, 1]], "k": -1},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 0]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 0]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
    ]
    for inst in targeted:
        check(inst, "targeted")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)

    print("tests_run:", tests_run)
    print("tests_passed:", tests_passed)
    print("failures:", len(failures))
    for fail in failures[:10]:
        print("FAIL", fail)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()

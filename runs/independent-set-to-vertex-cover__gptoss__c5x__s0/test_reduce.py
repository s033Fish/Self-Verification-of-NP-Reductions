"""Independent verification of reduce.py (Independent Set -> Vertex Cover).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def _max_independent_set_size(n, edges):
    """Largest size of a subset of 0..n-1 with no edge inside it."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    best = 0
    for mask in range(1 << n):
        ok = True
        # check no edge has both endpoints selected
        for u, v in edges:
            if (mask >> u) & 1 and (mask >> v) & 1:
                ok = False
                break
        if ok:
            size = bin(mask).count("1")
            if size > best:
                best = size
    return best


def solve_independent_set(instance):
    """Yes iff graph has an independent set of AT LEAST k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return _max_independent_set_size(n, instance["edges"]) >= k


def _min_vertex_cover_size(n, edges):
    """Smallest size of a vertex set covering every edge."""
    best = None
    for mask in range(1 << n):
        ok = True
        for u, v in edges:
            if not ((mask >> u) & 1 or (mask >> v) & 1):
                ok = False
                break
        if ok:
            size = bin(mask).count("1")
            if best is None or size < best:
                best = size
    return best if best is not None else 0


def solve_vertex_cover(instance):
    """Yes iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return _min_vertex_cover_size(n, instance["edges"]) <= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices (as edge lists)."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(possible) + 1):
        for chosen in itertools.combinations(possible, r):
            yield [list(e) for e in chosen]


def random_graph(n, rng, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def make_instance(n, edges, k):
    return {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src_ans = solve_independent_set(instance)
        try:
            IndependentSet.validate(instance)
        except Exception as exc:  # pragma: no cover
            failures.append((label, "source invalid: %r" % (exc,)))
            return
        target = reduce(instance)
        # target must be a valid VertexCover instance
        try:
            VertexCover.validate(target)
        except Exception as exc:
            failures.append((label, "target invalid: %r" % (exc,)))
            return
        tgt_ans = solve_vertex_cover(target)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, instance, target, src_ans, tgt_ans))

    # 1) Exhaustive over all graphs for n = 0..5 and all relevant k
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check(make_instance(n, edges, k), "exhaustive n=%d" % n)

    # 2) Random larger instances
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng, p=rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]))
        k = rng.randint(-3, n + 3)
        check(make_instance(n, edges, k), "random")

    # 3) Specific edge cases from the docstrings
    edge_cases = [
        make_instance(0, [], 0),
        make_instance(0, [], -5),
        make_instance(0, [], 1),
        make_instance(5, [], 0),
        make_instance(5, [], 5),
        make_instance(5, [], 6),
        make_instance(5, [], -1),
        make_instance(4, [[0, 1], [1, 2], [2, 3]], 2),
        make_instance(4, [[0, 1], [1, 2], [2, 3]], 3),
        make_instance(4, [[0, 1], [1, 2], [2, 3]], 1),
        make_instance(3, [[0, 1], [0, 2], [1, 2]], 1),
        make_instance(3, [[0, 1], [0, 2], [1, 2]], 2),
        make_instance(3, [[0, 1], [0, 2], [1, 2]], -1),
        make_instance(3, [[0, 1], [0, 2], [1, 2]], 4),
    ]
    for inst in edge_cases:
        check(inst, "edge-case")

    # 4) Confirm reduce is a pure function / doesn't mutate the input
    inst = make_instance(4, [[0, 1], [2, 3]], 1)
    snapshot = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}
    reduce(inst)
    tests_run += 1
    if inst == snapshot:
        tests_passed += 1
    else:
        failures.append(("input mutated", inst))

    # 5) Confirm output shape/keys exactly match the VertexCover format
    tests_run += 1
    out = reduce(make_instance(3, [[0, 1]], 1))
    if set(out.keys()) == {"n", "edges", "k"} and out["k"] == 2:
        tests_passed += 1
    else:
        failures.append(("output shape", out))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:10]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()

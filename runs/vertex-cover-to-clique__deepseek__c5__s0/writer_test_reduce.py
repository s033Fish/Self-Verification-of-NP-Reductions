"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

import itertools

from problems import VertexCover, Clique
from reduce import reduce
from solvers import vertex_cover_yes, clique_yes


def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]


def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive over all graphs with n in 0..5 and a range of k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                VertexCover.validate(inst)
                out = reduce(inst)
                Clique.validate(out)
                src = vertex_cover_yes(inst)
                tgt = clique_yes(out)
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((inst, out, src, tgt))

    # A few random-ish larger graphs, exhaustively over k.
    import random
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(6, 9)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        for k in range(-1, n + 2):
            inst = {"n": n, "edges": edges, "k": k}
            VertexCover.validate(inst)
            out = reduce(inst)
            Clique.validate(out)
            src = vertex_cover_yes(inst)
            tgt = clique_yes(out)
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                failures.append((inst, out, src, tgt))

    # Explicit edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},     # no vertices, no edges -> yes
        {"n": 0, "edges": [], "k": -1},    # k<0 -> no
        {"n": 1, "edges": [], "k": 0},     # yes
        {"n": 1, "edges": [], "k": 1},     # yes (k>=n)
        {"n": 3, "edges": [], "k": 0},     # no edges -> yes
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},  # needs cover of size 2 -> no
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},  # yes
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},  # no (two disjoint edges)
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},  # yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},  # path -> yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1},  # no
    ]
    for inst in cases:
        VertexCover.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        src = vertex_cover_yes(inst)
        tgt = clique_yes(out)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, out, src, tgt))

    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert not failures, f"{len(failures)} failures"
    return tests_run, tests_passed


if __name__ == "__main__":
    run()

"""Tests for reduce.py: exact solvers + exhaustive small-instance checks.

We verify the stronger statement minDS(reduce(G)) == minVC(G) + #isolated(G),
which implies the at-most-k equivalence for every k.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import VertexCover, DominatingSet


def min_vertex_cover(n, edges):
    """Exact minimum vertex cover size via branching on an uncovered edge."""
    adj_edges = [tuple(e) for e in edges]

    best = n

    def rec(covered, count):
        nonlocal best
        if count >= best:
            return
        # find an uncovered edge
        for u, v in adj_edges:
            if not (covered >> u) & 1 and not (covered >> v) & 1:
                rec(covered | (1 << u), count + 1)
                rec(covered | (1 << v), count + 1)
                return
        best = count

    rec(0, 0)
    return best


def min_dominating_set(n, edges):
    """Exact minimum dominating set size via branch and bound."""
    if n == 0:
        return 0
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    closed = [frozenset({v} | adj[v]) for v in range(n)]
    full = (1 << n) - 1
    best = n

    def rec(dominated, count):
        nonlocal best
        if count >= best:
            return
        if dominated == full:
            best = count
            return
        # pick an undominated vertex v; branch on v and each neighbour
        und = (~dominated) & full
        v = (und & -und).bit_length() - 1
        for u in sorted(closed[v]):
            mask = 0
            for x in closed[u]:
                mask |= 1 << x
            rec(dominated | mask, count + 1)

    rec(0, 0)
    return best


def isolated_count(n, edges):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return sum(1 for d in deg if d == 0)


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]


def check(src):
    VertexCover.validate(src)
    tgt = reduce(src)
    DominatingSet.validate(tgt)
    n, edges, k = src["n"], src["edges"], src["k"]
    mvc = min_vertex_cover(n, edges)
    mds = min_dominating_set(tgt["n"], tgt["edges"])
    iso = isolated_count(n, edges)
    assert mds == mvc + iso, (
        f"min-size mismatch src={src} tgt={tgt}: "
        f"minVC={mvc}, iso={iso}, minDS={mds}"
    )
    # at-most-k equivalence for every k in a broad range
    for kk in range(-2, n + 3):
        src_k = {"n": n, "edges": edges, "k": kk}
        tgt_k = reduce(src_k)
        assert (mvc <= kk) == (mds <= tgt_k["k"]), (
            f"answer mismatch src={src_k} -> tgt={tgt_k}: "
            f"VC={mvc <= kk}, DS={mds <= tgt_k['k']}"
        )


def main():
    tests_run = 0

    # Exhaustive over all graphs on 0..4 vertices (and all k).
    for n in range(0, 5):
        for edges in all_graphs(n):
            check({"n": n, "edges": edges, "k": 0})
            tests_run += 1

    # Random graphs on up to 9 vertices.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(e) for e in pairs[:m]]
        check({"n": n, "edges": edges, "k": 0})
        tests_run += 1

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1]], "k": -1},
        {"n": 3, "edges": [[0, 1]], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3]], "k": 2},
    ]
    for src in edge_cases:
        check(src)
        tests_run += 1

    print(f"tests_run={tests_run} tests_passed={tests_run}")
    return tests_run


if __name__ == "__main__":
    main()

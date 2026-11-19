"""Tests for the Independent Set -> Vertex Cover reduction."""

from __future__ import annotations

from itertools import combinations

from problems import IndependentSet, VertexCover
from reduce import reduce
from solvers import independent_set_yes, vertex_cover_yes


def all_graphs(n):
    """Yield every simple graph on n vertices as a list of edges."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [[u, v] for i, (u, v) in enumerate(possible) if mask >> i & 1]


def check_instance(inst, tests):
    IndependentSet.validate(inst)
    out = reduce(inst)
    VertexCover.validate(out)
    src = independent_set_yes(inst)
    tgt = vertex_cover_yes(out)
    tests.append((inst, out, src, tgt))
    assert src == tgt, f"MISMATCH: {inst} -> {out} ({src} vs {tgt})"


def main():
    tests = []
    # Exhaustive: all graphs on n = 0..5 vertices, all k in -2..n+2.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check_instance({"n": n, "edges": edges, "k": k}, tests)

    # A few larger random-ish structured cases with all k.
    import random

    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        possible = list(combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.4]
        for k in range(-2, n + 3):
            check_instance({"n": n, "edges": edges, "k": k}, tests)

    # Explicit edge cases.
    check_instance({"n": 0, "edges": [], "k": 0}, tests)
    check_instance({"n": 0, "edges": [], "k": -5}, tests)
    check_instance({"n": 0, "edges": [], "k": 1}, tests)
    check_instance({"n": 5, "edges": [], "k": 5}, tests)
    check_instance({"n": 5, "edges": [], "k": 6}, tests)
    # Complete graph K5: independent set max 1, vertex cover min 4.
    k5 = [[u, v] for u, v in combinations(range(5), 2)]
    check_instance({"n": 5, "edges": k5, "k": 1}, tests)
    check_instance({"n": 5, "edges": k5, "k": 2}, tests)

    print(f"tests_run={len(tests)} tests_passed={len(tests)}")
    return len(tests)


if __name__ == "__main__":
    main()

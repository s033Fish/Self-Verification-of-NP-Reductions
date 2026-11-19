"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance ``{"n": n, "edges": edges, "k": k}``, return
the Clique instance on the complement graph with target size ``n - k``.

Correctness: a vertex set ``S`` is a vertex cover of the source graph iff
``V \\ S`` is an independent set in the source graph, which holds iff
``V \\ S`` is a clique in the complement graph.  Thus a vertex cover of size
at most ``k`` exists iff the complement graph has a clique of size at least
``n - k``.

The construction runs in O(n^2) time and does not call any solver.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to a Clique instance."""
    n = instance["n"]
    k = instance["k"]

    # Normalize the source edges so membership tests are O(1).
    source_edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        source_edges.add((u, v))

    # The complement graph has an edge exactly where the source graph does not.
    complement_edges = [
        [u, v]
        for u in range(n)
        for v in range(u + 1, n)
        if (u, v) not in source_edges
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}

"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G = (V, E) iff V \\ S is a clique in the
complement graph complement(G).  Therefore G has a vertex cover of size
at most k iff complement(G) has a clique of size at least n - k.

The reduction keeps n, builds the complement edge list, and maps k to n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the complement graph on the same vertex set 0..n-1.
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}

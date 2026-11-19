"""Polynomial-time reduction from Clique to Vertex Cover.

A clique of size >= k in G is exactly an independent set of size >= k in G.
A set S is an independent set in G iff V \\ S is a vertex cover of the
complement graph G'.  Hence G has a clique of size >= k iff the complement
graph has a vertex cover of size <= n - k.

So the reduction maps (G, k) to (complement(G), n - k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the complement graph: all pairs {u, v}, u < v, not in G.
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}

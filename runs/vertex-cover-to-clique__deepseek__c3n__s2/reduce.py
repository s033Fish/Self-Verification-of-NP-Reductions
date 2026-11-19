"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G (every edge has an endpoint in S) iff its
complement V \\ S is an independent set of G, iff V \\ S is a clique in the
complement graph of G.

Therefore G has a vertex cover of size AT MOST k iff the complement graph
has a clique of size AT LEAST n - k.

The reduction maps (G, k) -> (complement(G), n - k), which is polynomial:
the complement has O(n^2) edges and can be built by scanning all pairs.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Clique instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the complement graph: edge {u, v} present iff it is absent in G.
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}

"""Polynomial-time reduction from Clique to Vertex Cover.

Reduction
---------
Given a Clique instance  G = (V, E), k  with |V| = n, produce the Vertex
Cover instance on the complement graph  G' = (V, E')  with

        E' = { {u, v} : u != v and {u, v} not in E }
        k' = n - k

Correctness
-----------
A set S of vertices is a clique in G  iff  S is an independent set in the
complement graph G' (every non-edge of G is an edge of G', so a clique of G
has no G' edges inside it, and vice versa).  A set C is a vertex cover of G'
iff V \\ C is an independent set of G'.  Therefore

    G has a clique of size >= k
        iff G' has an independent set of size >= k
        iff G' has a vertex cover of size <= n - k
        iff the produced Vertex Cover instance is a yes-instance.

The construction runs in O(n^2) time, i.e. polynomial in the input size.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Clique instance to an equivalent Vertex Cover instance."""
    n = instance["n"]
    k = instance["k"]

    # Normalise the edge set (undirected, no self loops, no duplicates).
    edges = set()
    for u, v in instance["edges"]:
        if u == v:
            continue
        edges.add((u, v) if u < v else (v, u))

    # Build the complement graph on the same vertex set.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edges:
                complement_edges.append([u, v])

    # Clique of size >= k in G  <=>  vertex cover of size <= n - k in G'.
    return {"n": n, "edges": complement_edges, "k": n - k}

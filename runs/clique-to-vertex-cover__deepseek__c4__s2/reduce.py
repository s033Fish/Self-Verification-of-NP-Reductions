"""Polynomial-time reduction from Clique to Vertex Cover.

Idea: A set S of vertices is a clique in G iff S is an independent set in the
complement graph G'.  A set C is a vertex cover of G' iff V \\ C is an
independent set of G'.  Hence G has a clique of size >= k iff G' has a vertex
cover of size <= n - k.

So the reduction maps (G, k) to (complement(G), n - k).

Edge cases:
  * k <= 0  -> k' = n - k >= n, and Vertex Cover is always yes for k' >= n.
  * k > n   -> k' = n - k < 0, and Vertex Cover is always no for k' < 0.
  * k = n   -> k' = 0, yes iff G' has no edges, i.e. G is complete, i.e. G has
               a clique of size n.
"""

from __future__ import annotations

from problems import Clique, VertexCover


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance."""
    Clique.validate(instance)

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

    result = {"n": n, "edges": complement_edges, "k": n - k}
    VertexCover.validate(result)
    return result

"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction
---------
Given a Vertex Cover instance (n, edges, k):

  * The Set Cover universe has one element per edge of the graph.
  * For every vertex v in 0..n-1 there is one set containing exactly the
    elements (edges) incident to v.
  * The budget k is copied unchanged.

A set of vertices covers every edge iff the corresponding collection of
vertex-sets covers every universe element, so the graph has a vertex cover
of size at most k iff the constructed set system has a set cover of size at
most k.  The construction is linear in the size of the input.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    universe_size = len(edges)

    # incident[v] = list of edge indices touching vertex v
    incident = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        incident[u].append(index)
        incident[v].append(index)

    sets = [list(edge_indices) for edge_indices in incident]

    return {"universe_size": universe_size, "sets": sets, "k": k}

"""Polynomial-time reduction from Vertex Cover to Set Cover.

Idea
----
Let the universe be the set of edges of the graph.  For every vertex v build
the set S_v = { index of edge e : v is an endpoint of e }.

A collection of at most k sets S_{v1}, ..., S_{vt} covers the universe
(i.e. every edge index) exactly when {v1, ..., vt} is a vertex cover of the
graph: an edge is covered by the chosen sets iff at least one of its endpoints
was chosen.  Hence the graph has a vertex cover of size <= k iff the produced
Set Cover instance has a set cover of size <= k.

Edge cases:
  * k < 0: both problems answer no (the target's k is copied unchanged).
  * no edges: universe_size = 0, target is yes for every k >= 0, matching
    the source (empty vertex cover).
  * k >= n: choosing all n vertex-sets covers every edge, so the target is
    yes, matching the source (all vertices form a vertex cover).

The construction is clearly polynomial: O(n + m) time and space.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Set Cover instance.

    The returned instance is yes exactly when the input instance is yes.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One set per vertex, holding the indices of its incident edges.
    sets: list[list[int]] = [[] for _ in range(n)]
    for edge_index, (u, v) in enumerate(edges):
        sets[u].append(edge_index)
        sets[v].append(edge_index)

    return {"universe_size": len(edges), "sets": sets, "k": k}

"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction (standard):
  * The universe is the set of edges of the graph: element i corresponds to
    edge edges[i].
  * For every vertex v in 0..n-1 there is one set S_v = { i : v is an endpoint
    of edges[i] }.
  * The budget k is unchanged.

A vertex cover C of size <= k covers every edge, i.e. the sets {S_v : v in C}
contain every universe element.  Conversely any collection of <= k sets that
covers the universe yields a vertex cover of size <= k (take the vertices of
the chosen sets; supersets only help).  Hence the answers agree.

The reduction is polynomial: O(n + m) sets/elements are produced.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One set per vertex, holding the indices of the edges incident to it.
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": len(edges), "sets": sets, "k": k}

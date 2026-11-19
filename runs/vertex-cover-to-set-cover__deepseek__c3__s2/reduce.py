"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction:
  * Each edge of the source graph becomes one element of the universe.
    Edge i (in the given order) becomes element i.
  * Each vertex v becomes one set: the set of edge-indices incident to v.
  * k is copied unchanged.

A vertex cover of size <= k chooses vertices whose incident-edge sets cover
every edge-element, i.e. a set cover of size <= k. Conversely any set cover
of size <= k selects vertices meeting every edge, i.e. a vertex cover.
"""

from __future__ import annotations


def reduce(instance):
    """Map a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    universe_size = len(edges)

    # sets[v] = list of edge indices incident to vertex v
    sets = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}

"""Polynomial-time reduction from Vertex Cover to Set Cover.

Idea (the standard incidence reduction):
  * The universe has one element per edge of the graph.
  * For every vertex v, create the set of all edges incident to v.
  * Keep the same budget k.

A set of vertices covers every edge iff the corresponding collection of
vertex-sets covers every edge-element, so the minimum vertex cover size
equals the minimum set cover size.  Hence the answer is preserved exactly,
including all the documented edge cases:

  * k < 0  -> both problems are "no".
  * no edges -> universe_size 0, which is "yes" for every k >= 0.
  * k >= n -> picking all n vertex-sets covers everything, so "yes".
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge, indexed by the edge's position.
    universe_size = len(edges)

    # sets[v] = indices of edges incident to vertex v.
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}

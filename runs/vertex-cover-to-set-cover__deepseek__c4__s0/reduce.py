"""Polynomial-time reduction from Vertex Cover to Set Cover.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
Set Cover instance:    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction: the universe is the set of edges (element i <-> edges[i]).  For each
vertex v we build the set of edges incident to v.  A set of vertices covers all
edges exactly when the corresponding collection of sets covers the universe, so
the same budget k works.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One set per vertex: the indices of the edges incident to that vertex.
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": len(edges), "sets": sets, "k": k}

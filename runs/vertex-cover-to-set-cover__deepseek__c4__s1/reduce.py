"""Polynomial-time reduction from Vertex Cover to Set Cover.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
Set Cover instance:    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction: make each edge an element of the universe, and for each vertex v
create a set containing exactly the edges incident to v.  A vertex cover of
size at most k picks at most k vertices whose incident-edge sets cover every
edge-element, and conversely any cover of the universe by at most k vertex-sets
selects at most k vertices covering every edge.  The budget k is unchanged.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Element i corresponds to edge i.
    universe_size = len(edges)

    incident: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        incident[u].append(index)
        incident[v].append(index)

    return {
        "universe_size": universe_size,
        "sets": incident,
        "k": k,
    }

"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction:
    Universe = the set of edges of the graph (element i <-> edges[i]).
    For every vertex v in 0..n-1 create a set S_v = { i : edge i is incident to v }.
    Keep k unchanged.

A vertex cover C covers every edge iff the collection {S_v : v in C} covers the
universe, so the graph has a vertex cover of size at most k iff the set system
has a set cover of size at most k.  The construction is linear time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge.
    universe_size = len(edges)

    # S_v collects the indices of all edges incident to vertex v.
    sets: list[list[int]] = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}

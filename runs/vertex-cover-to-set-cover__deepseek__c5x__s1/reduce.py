"""Polynomial-time reduction from Vertex Cover to Set Cover.

Reduction:
    Universe = the set of edges of the graph (edge i is element i).
    For each vertex v in 0..n-1 create a set S_v = { i : edge i is incident to v }.
    Keep k unchanged.

A set of vertices C covers every edge iff the corresponding sets {S_v : v in C}
cover the whole universe (all edges).  Hence the graph has a vertex cover of
size at most k iff the constructed Set Cover instance has a solution using at
most k sets.

Edge cases line up:
  * k < 0: both answers are no.
  * no edges: universe_size = 0, which is yes for every k >= 0.
  * k >= n: all n vertex-sets cover all edges, so yes.
  * every element (edge) belongs to at least one set (its endpoint), so there
    is never an uncovered-by-any-set element.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    num_edges = len(edges)
    sets: list[list[int]] = [[] for _ in range(n)]
    for edge_index, (u, v) in enumerate(edges):
        sets[u].append(edge_index)
        sets[v].append(edge_index)

    return {"universe_size": num_edges, "sets": sets, "k": k}

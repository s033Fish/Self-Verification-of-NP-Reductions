"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Given an undirected graph G with n vertices, we build G' as follows.

* If n <= 2 the source is always "no" (a simple graph needs at least three
  vertices to contain a cycle).  We return the always-"no" target instance
  {"n": 0, "edges": []}.

* Otherwise pick the vertex v = n-1 and split it into two copies v1 = n-1 and
  v2 = n, each adjacent to every neighbour of v.  Add two new leaves
  s = n+1 (attached to v1) and t = n+2 (attached to v2).  All other edges of
  G are kept unchanged.

Why this is an "iff":

  * If G has a Hamiltonian cycle v, a1, ..., a_{n-1}, v then
    s, v1, a1, ..., a_{n-1}, v2, t is a Hamiltonian path of G'.

  * Conversely, s and t are leaves, hence the two endpoints of any
    Hamiltonian path of G'.  Such a path is therefore
    s, v1, x1, ..., x_{n-1}, v2, t where {x1, ..., x_{n-1}} = V minus {v}.
    The edge v1-x1 forces x1 to be a neighbour of v, the edges x_i-x_{i+1}
    are edges of G and the edge x_{n-1}-v2 forces x_{n-1} to be a neighbour
    of v.  Hence v, x1, ..., x_{n-1}, v is a Hamiltonian cycle of G.

The construction uses O(n + m) time and space, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: source has no Hamiltonian cycle.  n = 0 is a "no" target instance.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = n - 1
    v1 = n - 1      # first copy of v
    v2 = n          # second copy of v
    s = n + 1       # leaf attached to v1
    t = n + 2       # leaf attached to v2

    new_edges: list[list[int]] = []
    for edge in edges:
        u, w = edge[0], edge[1]
        if u == v:
            new_edges.append([v1, w])
            new_edges.append([v2, w])
        elif w == v:
            new_edges.append([v1, u])
            new_edges.append([v2, u])
        else:
            new_edges.append([u, w])

    new_edges.append([s, v1])
    new_edges.append([t, v2])

    return {"n": n + 3, "edges": new_edges}

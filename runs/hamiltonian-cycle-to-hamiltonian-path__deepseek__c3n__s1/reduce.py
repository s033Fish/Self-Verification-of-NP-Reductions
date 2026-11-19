"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given an undirected graph G on vertices 0..n-1 with n >= 3, pick v = 0 and
create a new "twin" vertex v' = n whose neighbourhood is exactly N(v).
Then add two pendant leaves: a = n+1 attached to v, and b = n+2 attached
to v'.

Claim: G has a Hamiltonian cycle  <=>  H has a Hamiltonian path.

Why:
  * The leaves a and b have degree 1, so in any Hamiltonian path of H they
    must be the two endpoints.  Hence H has a Hamiltonian path iff the twin
    graph G' has a Hamiltonian path from v to v'.
  * (=>) If G has a Hamiltonian cycle, break it at v into a path
    a_1..a_{n-1} where a_1 and a_{n-1} are neighbours of v; then
    v - a_1 - ... - a_{n-1} - v' is a v-to-v' Hamiltonian path in G'.
  * (<=) If G' has a Hamiltonian path v - x_1 - ... - x_{n-1} - v', then
    x_{n-1} is a neighbour of v (v' is only adjacent to N(v)), so
    v - x_1 - ... - x_{n-1} - v is a Hamiltonian cycle of G.

For n < 3 the source answer is always no, so we return the trivially "no"
target instance {"n": 0, "edges": []}.

The construction is linear in the size of the input.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always "no" for n <= 2 (including n = 0).
    if n < 3:
        return {"n": 0, "edges": []}

    v = 0
    v_twin = n          # copy of v, adjacent to exactly the neighbours of v
    leaf_v = n + 1      # pendant attached to v
    leaf_twin = n + 2   # pendant attached to v_twin

    new_edges: list[list[int]] = [list(edge) for edge in edges]

    for u, w in edges:
        if u == v:
            new_edges.append([v_twin, w])
        elif w == v:
            new_edges.append([v_twin, u])

    new_edges.append([leaf_v, v])
    new_edges.append([leaf_twin, v_twin])

    return {"n": n + 3, "edges": new_edges}

"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with n = |V|:

* n == 0:  G has no path (no), so return an instance with no cycle
           ({"n": 0, "edges": []}).
* n == 1:  G has a path (yes), so return the triangle, which has a cycle.
* n >= 2:  Add one new vertex x = n joined to every vertex of G.
           G' = (V u {x}, E u {{x, v} : v in V}).

Correctness (n >= 2)
--------------------
(=>) If v1, ..., vn is a Hamiltonian path of G, then
     x, v1, ..., vn, x is a Hamiltonian cycle of G'.
(<=) Any Hamiltonian cycle of G' visits x.  Its two neighbours of x on the
     cycle are vertices of G; deleting x from the cycle leaves a path in G
     that visits every vertex of G exactly once.

The construction adds n edges and one vertex, so it runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # No Hamiltonian path exists; return an instance with no cycle.
        return {"n": 0, "edges": []}

    if n == 1:
        # The single vertex is a Hamiltonian path; return a yes cycle
        # instance (the triangle).
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a new universal vertex.
    new_vertex = n
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([new_vertex, v])
    return {"n": n + 1, "edges": new_edges}

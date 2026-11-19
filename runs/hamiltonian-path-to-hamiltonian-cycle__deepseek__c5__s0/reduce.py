"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Standard gadget: given G on n vertices, add one new vertex x connected to
every vertex of G.  Then G has a Hamiltonian path iff G' has a Hamiltonian
cycle:

  * A Hamiltonian path v1..vn of G extends to the cycle v1..vn-x-v1 in G'.
  * A Hamiltonian cycle of G' uses exactly two edges incident to x, say
    x-a and x-b; deleting x leaves a Hamiltonian path a..b of G.

Edge cases of the target definition force one special case:

  * n = 0: G' has 1 vertex and no edges -> no cycle.  Matches "n = 0 is no".
  * n = 1: HP is yes, but the gadget gives a 2-vertex graph, and the target
    says n <= 2 is always no.  So we map n = 1 to a triangle (yes).
  * n = 2: the gadget gives a triangle exactly when edge [0,1] is present,
    which matches the source's "n = 2 is yes iff [0,1] is present".
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 1 is a yes-instance of Hamiltonian Path, but the gadget would
    # produce a 2-vertex graph, which can never have a cycle.  Return a
    # fixed yes-instance (the triangle) instead.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [list(edge) for edge in edges]
    new_edges.extend([v, new_vertex] for v in range(n))

    return {"n": n + 1, "edges": new_edges}

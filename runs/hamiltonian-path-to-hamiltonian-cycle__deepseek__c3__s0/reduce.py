"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction (classic):
    Given G = (V, E) with V = {0, ..., n-1}, build G' by adding one new
    vertex x = n and connecting it to every vertex of G:
        V' = V u {x},   E' = E u { {x, v} : v in V }.

    Claim (for n >= 2): G has a Hamiltonian path  <=>  G' has a
    Hamiltonian cycle.

      (=>) If v1, v2, ..., vn is a Hamiltonian path of G, then
           x, v1, v2, ..., vn, x is a Hamiltonian cycle of G'.

      (<=) If C is a Hamiltonian cycle of G', it visits x; its two
           neighbours a, b on C are in V. Removing x from C leaves the
           path a, ..., b through all n vertices of G, i.e. a Hamiltonian
           path of G.

    Edge cases:
      * n = 0: source is no.  The construction gives a 1-vertex graph,
        which has no cycle, so it is also no.  (Handled explicitly.)
      * n = 1: source is yes (single vertex is a path).  The construction
        gives a 2-vertex graph, which can never have a cycle, so we must
        special-case it: return the triangle, which is yes.
      * n = 2: source is yes iff edge {0,1} exists.  The construction
        gives a 3-vertex graph; it is a triangle iff {0,1} exists, so the
        equivalence holds.  (Covered by the general case.)

The construction adds exactly n edges and one vertex, so it runs in
polynomial (linear) time and never calls any brute-force solver.
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: source is no; a 1-vertex graph is no as well.
    if n == 0:
        return {"n": 0, "edges": []}

    # n = 1: source is yes (the single vertex is a path).  The general
    # construction would yield a 2-vertex graph (always no), so return a
    # triangle instead, which is yes.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # General case n >= 2: add a new universal vertex x = n.
    new_edges = [list(edge) for edge in edges]
    new_edges.extend([n, v] for v in range(n))
    return {"n": n + 1, "edges": new_edges}

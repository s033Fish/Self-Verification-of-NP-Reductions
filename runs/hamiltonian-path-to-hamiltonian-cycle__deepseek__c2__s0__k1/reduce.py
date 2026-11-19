"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction (the standard one)
-------------------------------
Given a Hamiltonian Path instance ``G = (V, E)`` with ``V = {0, ..., n-1}``,
build a Hamiltonian Cycle instance ``G'`` by adding one brand-new vertex
``x = n`` and joining it to every vertex of ``G``:

    V' = V u {x}
    E' = E u { [v, x] : v in V }

Claim: G has a Hamiltonian path iff G' has a Hamiltonian cycle.

  * If ``v_0, v_1, ..., v_{n-1}`` is a Hamiltonian path of G, then
    ``x, v_0, v_1, ..., v_{n-1}, x`` is a Hamiltonian cycle of G'.
  * If G' has a Hamiltonian cycle, the new vertex ``x`` has neighbours only
    in V, so the cycle enters and leaves ``x`` through two distinct vertices
    of V; deleting ``x`` from the cycle leaves a Hamiltonian path of G.

The construction adds one vertex and n edges, so it runs in time linear in
the size of the input (polynomial).

Edge cases
----------
* n = 0: the source is "no"; the construction gives a 1-vertex graph, which
  is also "no" (a simple graph needs >= 3 vertices for a cycle).
* n = 1: the source is "yes" (a single vertex is a path), but the standard
  construction would give a 2-vertex graph, which can never have a cycle.
  We therefore map this case to the triangle, which is "yes".
* n = 2: the source is "yes" iff edge [0, 1] is present.  The construction
  yields the triangle when [0, 1] is present (yes) and the path
  0 - x - 1 otherwise (no), matching the source exactly.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance.

    The returned instance is "yes" for Hamiltonian Cycle exactly when the
    input is "yes" for Hamiltonian Path.  Runs in polynomial time and never
    calls a brute-force solver.
    """
    n = instance["n"]
    edges = instance["edges"]

    # n = 1 is the unique case where the standard gadget would be wrong:
    # the source is yes, but the gadget has only 2 vertices and so is no.
    # The triangle is a yes Hamiltonian Cycle instance.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # Standard gadget: add vertex x = n adjacent to every original vertex.
    x = n
    new_edges = [list(edge) for edge in edges]
    new_edges.extend([v, x] for v in range(n))
    return {"n": n + 1, "edges": new_edges}

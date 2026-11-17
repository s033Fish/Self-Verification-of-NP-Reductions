"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x(v,c) meaning "vertex v receives colour c".

* Exactly-one-colour per vertex: the positive 1-in-3 clause
      (x(v,0), x(v,1), x(v,2))
  forces exactly one of the three colours to be chosen for v.

* Different colours on an edge (u,v): for each colour c we must forbid
  x(u,c) and x(v,c) being true together.  Introduce a fresh auxiliary
  variable t(u,v,c) and add the positive 1-in-3 clause
      (x(u,c), x(v,c), t(u,v,c)).
  If x(u,c)=x(v,c)=true the clause already contains two true variables and
  can never be satisfied; otherwise t can be set to make exactly one true
  (t=false when exactly one of the two is true, t=true when both are false).
  Hence the projection of this clause onto x(u,c),x(v,c) is exactly
  "not both true".

Because each vertex has exactly one colour, the per-colour at-most-one
constraints are equivalent to the endpoints of every edge having different
colours.  The construction uses O(n + |E|) variables and clauses and is
clearly computable in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Vertex/colour variables: x(v, c) = 3*v + c + 1 for c in {0,1,2}.
    num_vars = 3 * n
    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([3 * v + 1, 3 * v + 2, 3 * v + 3])

    # Forbid equal colours on the endpoints of every edge, one fresh
    # auxiliary variable per (edge, colour).
    aux = num_vars
    for (u, v) in edges:
        for c in range(3):
            aux += 1
            clauses.append([3 * u + c + 1, 3 * v + c + 1, aux])

    return {"num_vars": aux, "clauses": clauses}

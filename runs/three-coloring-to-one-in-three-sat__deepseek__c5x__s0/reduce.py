"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} we introduce a variable
    x[v,c]  (variable id 3*v + c + 1)
which is true iff vertex v is assigned colour c.

* For every vertex v the clause
      [x[v,0], x[v,1], x[v,2]]
  is a 1-in-3 clause, so exactly one of the three colours is chosen for v.

* For every edge {u,w} and every colour c we introduce a fresh helper
  variable h and the clause
      [x[u,c], x[w,c], h].
  Because h occurs nowhere else, this clause is satisfiable (by a suitable
  choice of h) exactly when NOT both x[u,c] and x[w,c] are true, i.e. it
  forbids u and w from both receiving colour c.

Together the vertex clauses pick exactly one colour per vertex and the edge
clauses forbid equal colours on adjacent vertices, so the 1-in-3 formula is
satisfiable iff the graph is 3-colourable.

The construction uses 3*n + 3*|E| variables and n + 3*|E| clauses, hence runs
in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def xvar(vertex: int, colour: int) -> int:
        # variables 1..3n
        return 3 * vertex + colour + 1

    num_vars = 3 * n
    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([xvar(v, 0), xvar(v, 1), xvar(v, 2)])

    # Adjacent vertices must differ in every colour: forbid both endpoints
    # having colour c, using a fresh helper variable.
    for u, w in edges:
        for c in range(3):
            num_vars += 1
            helper = num_vars
            clauses.append([xvar(u, c), xvar(w, c), helper])

    return {"num_vars": num_vars, "clauses": clauses}

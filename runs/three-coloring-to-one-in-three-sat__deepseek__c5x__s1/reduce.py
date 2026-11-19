"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

SOURCE: {"n": n, "edges": [[u, v], ...]}
TARGET: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour c in {0,1,2} we introduce a boolean variable
x_{v,c} (1-indexed: 3*v + c + 1) meaning "vertex v has colour c".

* For every vertex v we add the clause [x_{v,0}, x_{v,1}, x_{v,2}].  A
  1-in-3 clause forces exactly one of these to be true, i.e. every vertex
  receives exactly one colour.

* For every edge {u,v} and every colour c we add a clause
      [x_{u,c}, x_{v,c}, z]
  where z is a fresh variable (a distinct one for every such clause).  If
  both x_{u,c} and x_{v,c} were true the clause would contain at least two
  true variables, which is impossible; hence the clause forbids the two
  endpoints sharing colour c.  Conversely, whenever not both are true, z can
  be chosen (0 if exactly one of the two is true, 1 if neither is) so that
  the clause has exactly one true variable.  Since each z occurs in exactly
  one clause it never constrains anything else.

The number of variables is 3*n + 3*|E| and the number of clauses is
n + 3*|E|, so the reduction is linear time / polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # Variables 1..3n are the vertex/colour variables, the remaining
    # 3*|E| variables are the per-edge-clause gadget variables.
    num_vars = 3 * n + 3 * len(edges)

    def color_var(vertex: int, color: int) -> int:
        return 3 * vertex + color + 1

    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([color_var(v, 0), color_var(v, 1), color_var(v, 2)])

    # Forbid both endpoints of an edge sharing a colour.
    for i, (u, v) in enumerate(edges):
        for c in range(3):
            fresh = 3 * n + 3 * i + c + 1
            clauses.append([color_var(u, c), color_var(v, c), fresh])

    return {"num_vars": num_vars, "clauses": clauses}

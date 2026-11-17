"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

SOURCE: {"n": n, "edges": [[u, v], ...]}
TARGET: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x(v, c) meaning "vertex v has colour c":

    x(v, c) = 3*v + c + 1

1. For every vertex v add the clause [x(v,0), x(v,1), x(v,2)].  A positive
   1-in-3 clause is satisfied iff exactly one of its variables is true, so
   this forces each vertex to receive exactly one colour.

2. For every edge {u, w} and every colour c add a fresh auxiliary variable t
   and the clause [x(u,c), x(w,c), t].  This clause is satisfiable iff x(u,c)
   and x(w,c) are not both true: if both were true the clause would already
   contain two true variables and no value of t could make exactly one true.
   Conversely, if at most one of them is true we can set t = true when both
   are false and t = false otherwise, making exactly one variable true.
   Hence these clauses enforce that an edge's endpoints never share a colour.

The auxiliary variables are independent of one another, so a proper 3-colouring
extends to a satisfying assignment and, conversely, the restriction of any
satisfying assignment to the x variables is a proper 3-colouring.

Number of variables: 3*n + 3*|E| (polynomial).  Number of clauses:
n + 3*|E| (polynomial).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses: list[list[int]] = []

    def x(vertex: int, colour: int) -> int:
        # Variables are 1-indexed.
        return 3 * vertex + colour + 1

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # Adjacent vertices must not share a colour.  A fresh auxiliary variable
    # turns "not both x(u,c) and x(w,c)" into a positive 1-in-3 clause.
    nxt = 3 * n + 1
    for edge in edges:
        u, w = edge
        for c in range(3):
            t = nxt
            nxt += 1
            clauses.append([x(u, c), x(w, c), t])

    return {"num_vars": num_vars, "clauses": clauses}

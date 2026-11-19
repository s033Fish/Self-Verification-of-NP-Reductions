"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Encoding
--------
For every vertex v and colour c in {0,1,2} introduce a boolean variable
    x(v, c)  =  "vertex v is coloured c".
These are the first 3*n variables (variable number 3*v + c + 1).

For every vertex v add the clause
    ( x(v,0), x(v,1), x(v,2) )
which is satisfied by a 1-in-3 assignment exactly when v gets exactly one
colour.

For every edge {u,w} and every colour c add a fresh auxiliary variable t and
the clause
    ( x(u,c), x(w,c), t ).
A 1-in-3 clause is satisfied iff exactly one of its three literals is true.
If both x(u,c) and x(w,c) were true the clause would have at least two true
literals and be unsatisfiable, so the clause forbids the two endpoints of an
edge from sharing colour c.  If at most one of them is true the auxiliary t is
forced (t = 1 iff both are false), so t never constrains anything else.

Hence a satisfying 1-in-3 assignment corresponds exactly to a proper
3-colouring and vice versa.

The construction uses 3*n + 3*|E| variables and n + 3*|E| clauses, so it runs
in linear (hence polynomial) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses: list[list[int]] = []

    def x(v: int, c: int) -> int:
        # variable 1..3n standing for "vertex v has colour c"
        return 3 * v + c + 1

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # Forbid equal colours on the endpoints of every edge.
    aux = 3 * n
    for u, w in edges:
        for c in range(3):
            aux += 1
            clauses.append([x(u, c), x(w, c), aux])

    assert aux == num_vars
    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Encoding
--------
For every vertex v and colour c in {0,1,2} we create a boolean variable
    x(v, c) = 1 + 3*v + c          (variables 1 .. 3n)
meaning "vertex v receives colour c".

For every vertex v we add the clause
    ( x(v,0), x(v,1), x(v,2) )
which, under the exactly-one-true semantics of 1-in-3-SAT, forces vertex v
to receive exactly one colour.

For every edge {u, w} and every colour c we add a fresh auxiliary variable
    aux = (next free variable)
and the clause
    ( x(u,c), x(w,c), aux ).

This clause is satisfiable iff NOT both x(u,c) and x(w,c) are true:
  * if x(u,c)=x(w,c)=1 the sum is at least 2, so no value of aux works;
  * if both are 0 we set aux=1;
  * if exactly one is 1 we set aux=0.
Hence the edge clauses forbid the two endpoints of an edge from sharing a
colour, exactly the 3-colouring requirement.

The formula is satisfiable iff the graph is 3-colourable, and the number of
variables is 3n + 3|E| while the number of clauses is n + 3|E|, so the
construction is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    clauses: list[list[int]] = []

    def x(v: int, c: int) -> int:
        return 1 + 3 * v + c

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    num_vars = 3 * n

    # Distinct colours on the endpoints of every edge.
    for u, w in edges:
        for c in range(3):
            num_vars += 1
            clauses.append([x(u, c), x(w, c), num_vars])

    return {"num_vars": num_vars, "clauses": clauses}

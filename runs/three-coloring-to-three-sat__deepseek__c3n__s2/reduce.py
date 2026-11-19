"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} we introduce a boolean
variable x(v, c), numbered  3*v + c + 1.  The intended meaning is
"vertex v receives colour c".

Clauses
-------
1. For each vertex v:  (x(v,0) v x(v,1) v x(v,2))
   -> every vertex gets at least one colour.  (3 literals, 3 variables.)

2. For each edge {u,v} and each colour c, the 2-literal constraint
   (~x(u,c) v ~x(v,c)) forbids both endpoints sharing colour c.  Since the
   target problem demands exactly 3 literals on 3 distinct variables, we
   pad each such constraint with a single shared helper variable y:
       (~x(u,c) v ~x(v,c) v  y)
       (~x(u,c) v ~x(v,c) v ~y)
   The pair is satisfiable iff ~x(u,c) v ~x(v,c) is: if both x(u,c) and
   x(v,c) were true, y would have to be both true and false.  Otherwise
   both clauses are satisfied regardless of y, so one global y suffices.

The result is satisfiable exactly when the graph is 3-colourable.  The
construction uses O(n + |E|) variables and clauses, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def _var(vertex: int, colour: int) -> int:
    """Variable number (1-based) for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    clauses: list[list[int]] = []

    # 1. Each vertex must receive at least one colour.
    for v in range(n):
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])

    # 2. Adjacent vertices must not share a colour.
    if edges:
        helper = 3 * n + 1  # single shared padding variable
        for u, v in edges:
            for c in range(3):
                a = _var(u, c)
                b = _var(v, c)
                clauses.append([-a, -b, helper])
                clauses.append([-a, -b, -helper])
        num_vars = helper
    else:
        num_vars = 3 * n

    return {"num_vars": num_vars, "clauses": clauses}

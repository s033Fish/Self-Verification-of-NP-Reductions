"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} we introduce a boolean
variable x_{v,c} meaning "vertex v receives colour c".  Numbering:

    x_{v,c}  =  3*v + c + 1          (variables 1..3n)

One extra variable y = 3n+1 is used only as a padding variable so that every
clause has exactly three literals on three different variables.

Clauses
-------
1. At least one colour per vertex:
       (x_{v,0} v x_{v,1} v x_{v,2})
2. At most one colour per vertex, for each pair c < d:
       (not x_{v,c} v not x_{v,d})
   A two-literal clause (a v b) is encoded as the pair
       (a v b v y) and (a v b v not y),
   which is equivalent to (a v b): for either value of y one of the two
   clauses reduces to (a v b), and if (a v b) holds both are satisfied.
3. For every edge (u,w) and every colour c, the endpoints may not share c:
       (not x_{u,c} v not x_{v,c})
   padded to three literals with the same y / not y trick.

Correctness
-----------
A proper 3-colouring gives a satisfying assignment (set x_{v,c} true iff v has
colour c, y true).  Conversely, in any satisfying assignment clauses of type 1
and 2 force exactly one colour per vertex, and clauses of type 3 forbid equal
colours on an edge, yielding a proper 3-colouring.  The construction uses
O(n + |E|) variables and clauses and runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 1
    pad = num_vars  # the single padding variable y

    def x(vertex: int, colour: int) -> int:
        return 3 * vertex + colour + 1

    clauses: list[list[int]] = []

    # 1. Every vertex gets at least one colour.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # 2. Every vertex gets at most one colour.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                a, b = -x(v, c), -x(v, d)
                clauses.append([a, b, pad])
                clauses.append([a, b, -pad])

    # 3. Adjacent vertices get different colours.
    for u, w in edges:
        for c in range(3):
            a, b = -x(u, c), -x(w, c)
            clauses.append([a, b, pad])
            clauses.append([a, b, -pad])

    return {"num_vars": num_vars, "clauses": clauses}

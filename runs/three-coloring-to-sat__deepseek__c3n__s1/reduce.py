"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding
--------
For each vertex v in 0..n-1 and each colour c in {0, 1, 2} we introduce a
boolean variable x(v, c), numbered  3*v + c + 1  (variables are 1..3n).

Variable x(v, c) is intended to mean "vertex v gets colour c".

Clauses
-------
1. For every vertex v:  [x(v,0), x(v,1), x(v,2)]
   (v must receive at least one colour.)
2. For every vertex v and every pair of distinct colours c < d:
       [-x(v,c), -x(v,d)]
   (v must not receive two colours at once.)
3. For every edge {u, w} and every colour c:
       [-x(u,c), -x(w,c)]
   (adjacent vertices must not share a colour.)

Correctness
-----------
A proper 3-colouring of the graph directly yields a satisfying assignment
(pick exactly the colour of each vertex; clauses 1 and 2 hold, and clause 3
holds because endpoints differ).  Conversely, any satisfying assignment can
be turned into a proper colouring: clause 1 forces at least one colour true
for each vertex, clause 2 forces at most one, so assign the unique true
colour; clause 3 guarantees adjacent vertices get different colours.

Size: 3n variables and n + 3n + 3|E| clauses, all produced in O(n + |E|)
time, so the reduction is polynomial.
"""

from __future__ import annotations

from typing import Any


def _var(vertex: int, colour: int) -> int:
    """Variable number (1-based) for 'vertex gets colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    for v in range(n):
        # At least one colour.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour.
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-_var(v, c), -_var(v, d)])

    for u, w in edges:
        # Endpoints of an edge differ.
        for c in range(3):
            clauses.append([-_var(u, c), -_var(w, c)])

    return {"num_vars": num_vars, "clauses": clauses}

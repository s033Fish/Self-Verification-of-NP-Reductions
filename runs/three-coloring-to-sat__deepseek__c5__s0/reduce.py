"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding
--------
For every vertex v in 0..n-1 and every colour c in {0,1,2} introduce a
boolean variable

    x(v, c)  =  3*v + c + 1          (variables are 1..3*n)

meaning "vertex v is assigned colour c".

Clauses
-------
1. For every vertex v:  (x(v,0) v x(v,1) v x(v,2))
   -> every vertex gets at least one colour.

2. For every edge {u,v} and every colour c:
       (~x(u,c) v ~x(v,c))
   -> the two endpoints of an edge never share a colour.

A proper 3-colouring of the graph yields a satisfying assignment by
setting x(v,c) true exactly for the colour of v, and conversely any
satisfying assignment gives each vertex a colour (pick any true colour)
that differs across every edge.  The construction uses O(n + m) clauses
of constant size, hence runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def _var(vertex: int, colour: int) -> int:
    """SAT variable index (1-based) for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    # Each vertex must receive at least one of the three colours.
    for v in range(n):
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

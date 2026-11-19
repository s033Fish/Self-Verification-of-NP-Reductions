"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} we introduce a boolean
variable x[v][c] meaning "vertex v has colour c".  The variables are numbered

    x(v, c) = 3*v + c + 1        (so variables 1..3n are used).

One extra variable d = 3n+1 is used to pad 2-literal clauses.

Clauses
-------
  * At least one colour per vertex:
        ( x(v,0) OR x(v,1) OR x(v,2) )
    exactly 3 literals on 3 distinct variables.

  * For every edge {u,w} and every colour c, the endpoints must not share c:
        ( NOT x(u,c) OR NOT x(w,c) )
    This has only 2 literals, so it is padded with the shared variable d:
        ( NOT x(u,c) OR NOT x(w,c) OR  d )
        ( NOT x(u,c) OR NOT x(w,c) OR NOT d )
    For a fixed value of d one of these two clauses is exactly the original
    2-clause and the other is trivially true, so the pair is equivalent to
    the original 2-clause.  Sharing d across all pairs is fine because the
    equivalence holds for every fixed value of d.

Why the "at most one colour per vertex" clauses are unnecessary
---------------------------------------------------------------
If the formula is satisfiable then every vertex has at least one true colour
and, for every edge {u,w}, no colour is true for both endpoints.  Picking for
each vertex any one of its true colours therefore gives a proper 3-colouring.
Conversely any proper 3-colouring extends to a satisfying assignment.  Hence
the formula is satisfiable iff the graph is 3-colourable.

The construction is clearly polynomial: O(n + |E|) clauses and 3n+1
variables.
"""

from __future__ import annotations

from problems import ThreeColoring


def reduce(instance: dict) -> dict:
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    ThreeColoring.validate(instance)

    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 1          # x(v,c) = 3v+c+1, plus shared padding var d
    d = num_vars
    clauses: list[list[int]] = []

    for v in range(n):
        base = 3 * v + 1
        clauses.append([base, base + 1, base + 2])

    for u, w in edges:
        for c in range(3):
            a = -(3 * u + c + 1)
            b = -(3 * w + c + 1)
            clauses.append([a, b, d])
            clauses.append([a, b, -d])

    return {"num_vars": num_vars, "clauses": clauses}

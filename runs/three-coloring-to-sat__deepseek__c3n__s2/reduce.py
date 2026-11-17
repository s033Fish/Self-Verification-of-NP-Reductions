"""Polynomial-time reduction from 3-Coloring to SAT.

Variable encoding: for vertex v (0..n-1) and colour c (0..2) we introduce a
Boolean variable x_{v,c} meaning "vertex v gets colour c".  The variables are
numbered 1..3n via  var(v, c) = 3*v + c + 1.

Clauses:
  * for every vertex v:  (x_{v,0} v x_{v,1} v x_{v,2})        at least one colour
  * for every vertex v and colours c < d:
        (~x_{v,c} v ~x_{v,d})                               at most one colour
  * for every edge [u, w] and colour c:
        (~x_{u,c} v ~x_{w,c})                               endpoints differ

A satisfying assignment of the formula corresponds exactly to a proper
3-colouring, and vice versa.  For n = 0 the formula has no variables and no
clauses, which is satisfiable (yes), matching the source edge case.

The reduction is O(n^2) in the number of vertices (at most 3n + 3n + 3|E|
clauses), hence polynomial time.  No brute-force solver is called.
"""

from __future__ import annotations

from typing import Any

COLOURS = (0, 1, 2)


def _var(vertex: int, colour: int) -> int:
    """Variable index (1-based) for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a SAT instance.

    Input : {"n": n, "edges": [[u, v], ...]}
    Output: {"num_vars": 3*n, "clauses": [[literal, ...], ...]}
    """
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    for v in range(n):
        # At least one colour for v.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour for v.
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-_var(v, c), -_var(v, d)])

    for edge in edges:
        u, w = edge
        for c in COLOURS:
            # Adjacent vertices may not share colour c.
            clauses.append([-_var(u, c), -_var(w, c)])

    return {"num_vars": num_vars, "clauses": clauses}

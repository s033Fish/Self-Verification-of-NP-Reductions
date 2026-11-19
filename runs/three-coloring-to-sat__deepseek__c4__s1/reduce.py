"""Polynomial-time reduction from 3-Coloring to SAT.

Variable numbering: for vertex v in 0..n-1 and colour c in 0..2, the
variable x(v,c) = 3*v + c + 1 means "vertex v gets colour c".

Clauses:
  * For every vertex v: (x(v,0) or x(v,1) or x(v,2))          -- at least one colour
  * For every vertex v and colours c < d: (~x(v,c) or ~x(v,d)) -- at most one colour
  * For every edge {u,v} and colour c: (~x(u,c) or ~x(v,c))    -- endpoints differ

The formula is satisfiable iff the graph is 3-colourable.  The reduction
uses O(n + m) variables/clauses and runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def _var(v: int, c: int) -> int:
    """SAT variable (1-based) for 'vertex v has colour c'."""
    return 3 * v + c + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a SAT instance.

    instance: {"n": n, "edges": [[u, v], ...]}
    returns:  {"num_vars": m, "clauses": [[literal, ...], ...]}
    """
    n = instance["n"]
    edges = instance["edges"]

    clauses: list[list[int]] = []

    for v in range(n):
        # At least one colour.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour.
        clauses.append([-_var(v, 0), -_var(v, 1)])
        clauses.append([-_var(v, 0), -_var(v, 2)])
        clauses.append([-_var(v, 1), -_var(v, 2)])

    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

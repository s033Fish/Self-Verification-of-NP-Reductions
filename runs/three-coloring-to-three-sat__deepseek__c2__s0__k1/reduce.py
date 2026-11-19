"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

For every vertex v and colour c in {0, 1, 2} we introduce a Boolean
variable x_{v,c} meaning "vertex v has colour c".  Variable numbers are
1-based: x_{v,c} is 3*v + c + 1.

Clauses:
  * For every vertex v, the clause (x_{v,0} or x_{v,1} or x_{v,2})
    says v gets at least one colour.
  * For every edge {u, v} and every colour c, the two endpoints may not
    both have colour c.  This is the 2-literal constraint
    (~x_{u,c} or ~x_{v,c}).  To fit the target format, which requires
    exactly three literals on three different variables, we introduce a
    fresh auxiliary variable y and use the equisatisfiable pair
        (~x_{u,c} or ~x_{v,c} or  y)
        (~x_{u,c} or ~x_{v,c} or ~y)
    (if both x's are true these force y and ~y; otherwise both clauses
    are satisfied regardless of y).

A satisfying assignment corresponds to assigning each vertex a set of
colours: adjacent vertices receive disjoint non-empty sets.  Picking one
colour from each set then yields a proper 3-colouring, and conversely a
proper 3-colouring gives singleton sets.  Hence the reduction preserves
the answer.  The number of variables and clauses is linear in n + |E|,
so the reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an equisatisfiable 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def var(vertex: int, colour: int) -> int:
        # 1-based variable number for "vertex has colour".
        return 3 * vertex + colour + 1

    clauses: list[list[int]] = []

    # Every vertex gets at least one colour.
    for vertex in range(n):
        clauses.append([var(vertex, 0), var(vertex, 1), var(vertex, 2)])

    # Every edge forbids equal colours at its two endpoints.
    next_var = 3 * n
    for u, v in edges:
        for colour in range(3):
            next_var += 1
            y = next_var
            clauses.append([-var(u, colour), -var(v, colour), y])
            clauses.append([-var(u, colour), -var(v, colour), -y])

    return {"num_vars": next_var, "clauses": clauses}

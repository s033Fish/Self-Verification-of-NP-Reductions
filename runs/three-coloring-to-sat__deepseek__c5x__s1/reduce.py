"""Polynomial-time reduction from 3-Coloring to SAT.

Variable encoding: for vertex v in 0..n-1 and colour c in {0,1,2} we use the
SAT variable

    x(v, c) = 3*v + c + 1        (variables are 1..3n)

with the intended meaning "vertex v receives colour c".

Clauses:
  * for every vertex v:      (x(v,0) v x(v,1) v x(v,2))          -- some colour
  * for every vertex v and every pair c<d:
                             (~x(v,c) v ~x(v,d))                -- at most one colour
  * for every edge {u,w} and every colour c:
                             (~x(u,c) v ~x(w,c))                -- endpoints differ

The formula is satisfiable iff the graph is 3-colourable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a 3-Coloring instance to a SAT (CNF) instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    def var(v: int, c: int) -> int:
        return 3 * v + c + 1

    for v in range(n):
        # at least one colour
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # at most one colour
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    for u, w in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(w, c)])

    return {"num_vars": num_vars, "clauses": clauses}

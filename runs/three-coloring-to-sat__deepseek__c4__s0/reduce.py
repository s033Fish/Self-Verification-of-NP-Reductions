"""Polynomial-time reduction from 3-Coloring to SAT.

Variable encoding: for vertex v in 0..n-1 and colour c in {0,1,2} we use
    x(v, c) = 3*v + c + 1        (so num_vars = 3*n)

Clauses:
  * For every vertex v:  [x(v,0), x(v,1), x(v,2)]
        at least one colour is chosen for v.
  * For every vertex v and colour pair c < d:  [-x(v,c), -x(v,d)]
        at most one colour is chosen for v.
  * For every edge (u,v) and every colour c:  [-x(u,c), -x(v,c)]
        endpoints of an edge must not share a colour.

A satisfying assignment corresponds exactly to a proper 3-colouring, and
vice versa.  The construction is O(n^2 + m) time and space.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    def var(v: int, c: int) -> int:
        return 3 * v + c + 1

    clauses: list[list[int]] = []

    for v in range(n):
        # at least one colour
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # at most one colour
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

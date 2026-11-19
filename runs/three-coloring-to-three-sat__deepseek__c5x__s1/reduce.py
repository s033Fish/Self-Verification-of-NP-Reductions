"""Polynomial-time reduction from 3-Coloring to 3-SAT.

SOURCE: ThreeColoring instance {"n": n, "edges": [[u, v], ...]}
TARGET: ThreeSat instance {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce the boolean
variable x_{v,c} (meaning "vertex v has colour c").  Map it to the 1-based
variable index

        var(v, c) = 1 + 3*v + c          (so variables 1..3n are used)

Clauses:
  * For each vertex v:  (x_{v,0} v x_{v,1} v x_{v,2})
        -> every vertex gets at least one colour.  Already 3 literals.
  * For each vertex v and each pair c < d:
        (not x_{v,c} v not x_{v,d})
        -> a vertex gets at most one colour.
  * For each edge {u,w} and each colour c:
        (not x_{u,c} v not x_{v,c})
        -> the endpoints of an edge get different colours.

The last two families are 2-literal clauses.  A 2-clause (a v b) is replaced
by the two 3-literal clauses

        (a v b v z)   and   (a v b v not z)

where z is one single fresh variable (index 3n+1) shared by all padded
clauses.  The pair is equivalent to (a v b): if a v b is true both clauses are
satisfied; if a v b is false the pair forces z and not z simultaneously, which
is impossible.  Because the pair is equivalent to the original 2-clause, and
all padded pairs share the same z, the whole formula is satisfiable iff the
original 3-colouring formula is.  Every produced clause has exactly 3 literals
on 3 distinct variables.

The construction uses 3n+1 variables and O(n + |E|) clauses, so it runs in
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # Variable index for "vertex v has colour c" (1-based, colours 0,1,2).
    def var(v: int, c: int) -> int:
        return 1 + 3 * v + c

    # Single fresh padding variable.
    z = 3 * n + 1
    num_vars = z  # variables 1..3n+1 (z may be unused if there is nothing to pad)

    clauses: list[list[int]] = []

    # At least one colour per vertex (already exactly 3 literals).
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # At most one colour per vertex, padded to 3 literals.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                a = -var(v, c)
                b = -var(v, d)
                clauses.append([a, b, z])
                clauses.append([a, b, -z])

    # Edge endpoints must differ, padded to 3 literals.
    for edge in edges:
        u, w = edge
        for c in range(3):
            a = -var(u, c)
            b = -var(w, c)
            clauses.append([a, b, z])
            clauses.append([a, b, -z])

    return {"num_vars": num_vars, "clauses": clauses}

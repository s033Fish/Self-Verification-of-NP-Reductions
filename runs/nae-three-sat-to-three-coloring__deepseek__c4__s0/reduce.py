"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Fix a triangle on vertices T=0, F=1, R=2.  The three colours of any proper
3-colouring of this triangle are distinct; think of colour(T) as "true" and
colour(F) as "false", while colour(R) is a neutral "base" colour.

For every variable v in 1..m create two vertices pos(v) and neg(v) and add
the edges (pos(v), neg(v)), (pos(v), R), (neg(v), R).  Because both are
adjacent to R they never receive colour(R), and because they are adjacent to
each other they receive the two remaining colours in some order: exactly one
of them gets colour(T) (true) and the other colour(F) (false).

For every clause (l1, l2, l3) create three fresh vertices p, q, r forming a
triangle (p,q,r) and connect p to the vertex of l1, q to the vertex of l2 and
r to the vertex of l3.

Claim: the clause gadget is 3-colourable iff the three literal vertices are
not all equal (i.e. the clause is NAE-satisfied).
  * If all three literals have the same colour c (c is colour(T) or colour(F)),
    then p, q, r must each avoid c, leaving only two colours for three
    pairwise-adjacent vertices -- impossible.
  * Otherwise at least one literal is colour(T) and at least one is colour(F).
    A short case check gives a valid colouring of p, q, r; e.g. if the literal
    colours are (T,T,F) use (p,q,r) = (F,R,T); if (T,F,F) use (F,T,R); the
    remaining mixed cases follow by symmetry.

Hence the whole graph is 3-colourable iff the formula has a NAE-satisfying
assignment.  The construction uses O(m + #clauses) vertices and edges.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    T, F, R = 0, 1, 2
    edges: list[tuple[int, int]] = [(T, F), (F, R), (T, R)]

    def pos(v: int) -> int:
        return 3 + 2 * (v - 1)

    def neg(v: int) -> int:
        return 4 + 2 * (v - 1)

    for v in range(1, num_vars + 1):
        p, q = pos(v), neg(v)
        edges.append((p, q))
        edges.append((p, R))
        edges.append((q, R))

    n = 3 + 2 * num_vars

    for clause in clauses:
        p, q, r = n, n + 1, n + 2
        n += 3
        edges.append((p, q))
        edges.append((q, r))
        edges.append((p, r))
        lit_vertices = [
            pos(lit) if lit > 0 else neg(-lit) for lit in clause
        ]
        edges.append((p, lit_vertices[0]))
        edges.append((q, lit_vertices[1]))
        edges.append((r, lit_vertices[2]))

    return {"n": n, "edges": [[u, v] for (u, v) in edges]}

"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Construction
------------
Palette: three vertices T=0, F=1, B=2 forming a triangle, so they receive
three distinct colours.  We read "colour of T" as TRUE and "colour of F" as
FALSE.

Variable v: two vertices x_v and nx_v joined to each other and both joined to
B.  Hence x_v and nx_v get the two colours {T,F} and are opposite: exactly one
of them is TRUE.  Literal +v is represented by x_v, literal -v by nx_v.

Clause (l0 or l1 or l2): four fresh aux vertices a,b,c,d plus the shared T
vertex, with edges
    a-d, b-c, c-d, a-l2, b-l0, c-l1, d-l0, a-T, b-T.
This gadget is 3-colourable (with the literal vertices fixed to T/F) exactly
when at least one of l0,l1,l2 is coloured T, i.e. exactly when the clause is
satisfied.  (Verified exhaustively over all 8 truth assignments of the three
literals.)

The whole graph is 3-colourable iff there is a satisfying assignment.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    T, F, B = 0, 1, 2
    edges: set[tuple[int, int]] = set()

    def add(u: int, v: int) -> None:
        if u == v:
            return
        edges.add((u, v) if u < v else (v, u))

    # palette triangle
    add(T, F)
    add(F, B)
    add(T, B)

    next_id = 3
    pos: dict[int, int] = {}
    neg: dict[int, int] = {}
    for v in range(1, num_vars + 1):
        pos[v] = next_id
        neg[v] = next_id + 1
        next_id += 2
        add(pos[v], neg[v])
        add(pos[v], B)
        add(neg[v], B)

    def lit_node(lit: int) -> int:
        return pos[lit] if lit > 0 else neg[-lit]

    for clause in clauses:
        a, b, c, d = next_id, next_id + 1, next_id + 2, next_id + 3
        next_id += 4
        l0, l1, l2 = (lit_node(l) for l in clause)
        add(a, d)
        add(b, c)
        add(c, d)
        add(a, l2)
        add(b, l0)
        add(c, l1)
        add(d, l0)
        add(a, T)
        add(b, T)

    return {"n": next_id, "edges": [list(e) for e in sorted(edges)]}

"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Start with a base triangle on vertices T=0, F=1, B=2.  In any proper
3-colouring these three vertices receive the three distinct colours; we
name them so that colour(T) is "true", colour(F) is "false" and colour(B)
is a neutral colour.

For every variable v (1..m) create two vertices pos_v and neg_v, both
adjacent to B and to each other.  Since B has the neutral colour, pos_v and
neg_v must take the two remaining colours, i.e. one is "true" and the other
"false".  Thus a colouring encodes a truth assignment: literal vertex has
colour(T) iff the literal is true.

For every clause (l1,l2,l3) create a fresh triangle x,y,z and join the
vertex of l1 to x, l2 to y and l3 to z.  A triangle needs three distinct
colours, so x,y,z get all three colours.  If the three literals all had the
same colour (all true or all false), then x,y,z would each have to avoid
that single colour and would need three distinct colours from only two
remaining colours -- impossible.  Conversely, whenever the three literals
are not all equal, x,y,z can always be coloured with the three distinct
colours avoiding the respective literal colours (checked case by case over
the six not-all-equal patterns).

Hence the graph is 3-colourable iff the formula has a not-all-equal
satisfying assignment.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: T = true colour, F = false colour, B = neutral colour.
    T, F, B = 0, 1, 2
    n = 3
    edges: list[list[int]] = [[T, F], [F, B], [B, T]]

    pos: dict[int, int] = {}
    neg: dict[int, int] = {}
    for v in range(1, num_vars + 1):
        p = n
        q = n + 1
        n += 2
        pos[v] = p
        neg[v] = q
        edges.append([p, B])
        edges.append([q, B])
        edges.append([p, q])

    def literal_vertex(literal: int) -> int:
        v = abs(literal)
        return pos[v] if literal > 0 else neg[v]

    for clause in clauses:
        x, y, z = n, n + 1, n + 2
        n += 3
        edges.append([x, y])
        edges.append([y, z])
        edges.append([z, x])
        edges.append([literal_vertex(clause[0]), x])
        edges.append([literal_vertex(clause[1]), y])
        edges.append([literal_vertex(clause[2]), z])

    return {"n": n, "edges": edges}

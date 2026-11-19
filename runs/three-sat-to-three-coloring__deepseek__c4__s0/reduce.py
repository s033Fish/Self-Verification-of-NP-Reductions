"""Polynomial-time reduction from 3-SAT to 3-Coloring.

SOURCE: ThreeSat  {"num_vars": m, "clauses": [[l1,l2,l3], ...]}
TARGET: ThreeColoring  {"n": n, "edges": [[u,v], ...]}

Construction
------------
Palette: three mutually adjacent vertices
    T = 0 (colour "true"), F = 1 (colour "false"), B = 2 (colour "base").

Variable gadget: for variable i (1..m) two vertices
    xt(i) = 3 + 2*(i-1)      ("x_i is true")
    xf(i) = 3 + 2*(i-1) + 1  ("x_i is false")
with edges (xt, xf), (xt, B), (xf, B).  Since both are adjacent to B and to
each other they must receive the two colours T and F in some order; the
choice encodes the truth value of x_i.

Clause gadget: for a clause, three fresh vertices u1,u2,u3 forming a triangle,
with u_j adjacent to the literal vertex of the j-th literal.  If all three
literals are coloured F then no u_j may be F, so the triangle would need three
distinct colours from {T,B} -- impossible.  If at least one literal is T the
triangle can always be coloured (assign the three distinct colours so that
u_j != colour(literal_j)).

The literal vertex of +i is xt(i); the literal vertex of -i is xf(i).

The graph is 3-colourable iff the formula is satisfiable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Palette vertices.
    TRUE, FALSE, BASE = 0, 1, 2
    edges: list[list[int]] = [
        [TRUE, FALSE],
        [TRUE, BASE],
        [FALSE, BASE],
    ]

    def lit_true(v: int) -> int:
        return 3 + 2 * (v - 1)

    def lit_false(v: int) -> int:
        return 3 + 2 * (v - 1) + 1

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        t = lit_true(v)
        f = lit_false(v)
        edges.append([t, f])
        edges.append([t, BASE])
        edges.append([f, BASE])

    # Clause gadgets.
    next_vertex = 3 + 2 * num_vars
    for clause in clauses:
        u1, u2, u3 = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        edges.append([u1, u2])
        edges.append([u2, u3])
        edges.append([u1, u3])
        for u, literal in zip((u1, u2, u3), clause):
            var = abs(literal)
            node = lit_true(var) if literal > 0 else lit_false(var)
            edges.append([u, node])

    return {"n": next_vertex, "edges": edges}

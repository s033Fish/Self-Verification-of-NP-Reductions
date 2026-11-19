"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Encoding
--------
Truth values are encoded with colours.  We build one shared "base" vertex
(vertex 0).  For every variable v (1..m) we create two vertices

    pos(v) = 2v - 1      neg(v) = 2v

and add the triangle edges

    base - pos(v), base - neg(v), pos(v) - neg(v).

Hence pos(v) and neg(v) always receive the two colours different from the
colour of base, and they differ from each other.  Interpreting one of those
two colours as "true" and the other as "false", every truth assignment of
the variables corresponds to such a colouring and vice versa.

For every clause (l1, l2, l3) we add three fresh vertices g0, g1, g2 that
form a triangle, and connect gi to the vertex representing li.  If the
three literal vertices all had the same colour, then g0, g1, g2 would all
have to avoid that colour and be pairwise different, impossible with only
two remaining colours.  If the literals are not all equal, a valid colouring
of the gadget exists (e.g. for literals A, A, B use g0=B, g1=C, g2=A).
Thus the clause gadget is 3-colourable exactly when its literals are not
all equal, i.e. exactly when the NAE clause is satisfied.

The graph is 3-colourable iff the formula is satisfiable.  The reduction is
linear in the size of the instance.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    def add(u: int, v: int) -> None:
        edges.append([u, v])

    base = 0

    def pos(v: int) -> int:
        return 2 * v - 1

    def neg(v: int) -> int:
        return 2 * v

    # Variable gadgets: a triangle base / pos(v) / neg(v).
    for v in range(1, num_vars + 1):
        add(base, pos(v))
        add(base, neg(v))
        add(pos(v), neg(v))

    next_vertex = 2 * num_vars + 1

    # Clause gadgets: a triangle attached to the three literal vertices.
    for clause in clauses:
        g0, g1, g2 = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        add(g0, g1)
        add(g1, g2)
        add(g0, g2)
        for gadget_vertex, literal in zip((g0, g1, g2), clause):
            variable = abs(literal)
            literal_vertex = pos(variable) if literal > 0 else neg(variable)
            add(gadget_vertex, literal_vertex)

    return {"n": next_vertex, "edges": edges}

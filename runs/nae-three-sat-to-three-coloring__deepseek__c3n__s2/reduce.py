"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

SOURCE: NaeThreeSat   instance {"num_vars": m, "clauses": [[l1,l2,l3], ...]}
TARGET: ThreeColoring instance {"n": n, "edges": [[u,v], ...]}

Idea
----
Use three colours: T, F and B.  A single *base* vertex is coloured B.
For every variable v we create two vertices pos[v] and neg[v].  Both are
joined to the base and to each other, so they must receive the two colours
different from B, i.e. {T, F}: one of them is T and the other is F.  Reading
pos[v] == T as "v is true" therefore makes every literal vertex carry the
colour T exactly when the literal is true and F exactly when it is false.

For every clause we add a fresh triangle a, b, c (three mutually adjacent
vertices, which therefore use all three colours) and join a, b, c to the
literal vertices of the clause's three literals.  Because a triangle vertex
cannot share a colour with the literal it is attached to, the triangle can
be coloured iff the three literal colours are not all equal, i.e. iff the
clause has at least one true and at least one false literal.

Hence the formula is NAE-satisfiable iff the graph is 3-colourable.
The construction uses O(m + #clauses) vertices and edges, so it is
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex layout:
    #   0                       : base vertex (colour B)
    #   2v-1  for v = 1..m      : positive literal vertex of variable v
    #   2v    for v = 1..m      : negative literal vertex of variable v
    #   2m+1 ...                : three fresh vertices per clause (a triangle)
    base = 0
    pos = {v: 2 * v - 1 for v in range(1, num_vars + 1)}
    neg = {v: 2 * v for v in range(1, num_vars + 1)}

    edges: list[list[int]] = []
    seen: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        add_edge(base, pos[v])
        add_edge(base, neg[v])
        add_edge(pos[v], neg[v])

    def literal_vertex(lit: int) -> int:
        if lit > 0:
            return pos[lit]
        return neg[-lit]

    next_vertex = 2 * num_vars + 1
    for clause in clauses:
        a, b, c = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        # The clause triangle must use all three colours.
        add_edge(a, b)
        add_edge(b, c)
        add_edge(a, c)
        # Each triangle vertex is adjacent to its literal vertex, so it cannot
        # take that literal's colour.
        add_edge(a, literal_vertex(clause[0]))
        add_edge(b, literal_vertex(clause[1]))
        add_edge(c, literal_vertex(clause[2]))

    return {"n": next_vertex, "edges": edges}

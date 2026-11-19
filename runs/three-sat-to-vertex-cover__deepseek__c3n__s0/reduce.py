"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Variable gadget: for each variable v in 1..m create two vertices
    t_v = 2*(v-1)      (represents "v is true")
    f_v = 2*(v-1) + 1  (represents "v is false")
joined by an edge, so any vertex cover must pick at least one of them.

Clause gadget: for each clause create a triangle on three fresh vertices,
one per literal.  A vertex cover must pick at least two vertices of each
triangle.

Connection: the clause vertex for literal l is joined to the variable
vertex that represents l being FALSE (for literal +v -> f_v, for -v -> t_v).
Thus if a clause vertex is left out of the cover, the corresponding literal
must be true.

Set k = m + 2 * (#clauses).  The formula is satisfiable iff the graph has a
vertex cover of size at most k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    # Variable gadgets: vertices 2*(v-1) [true] and 2*(v-1)+1 [false].
    def true_vertex(var: int) -> int:
        return 2 * (var - 1)

    def false_vertex(var: int) -> int:
        return 2 * (var - 1) + 1

    for v in range(1, num_vars + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    # Clause gadgets: triangles of three fresh vertices each.
    next_vertex = 2 * num_vars
    for clause in clauses:
        base = next_vertex
        next_vertex += 3
        a, b, c = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for literal, vertex in zip(clause, (a, b, c)):
            var = abs(literal)
            # Literal is true when (literal > 0 and v true) or (literal < 0 and v false).
            # Connect to the variable vertex that makes the literal false.
            if literal > 0:
                edges.append([vertex, false_vertex(var)])
            else:
                edges.append([vertex, true_vertex(var)])

    k = num_vars + 2 * len(clauses)
    return {"n": next_vertex, "edges": edges, "k": k}

"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction (the classic Garey--Johnson reduction):

* For every variable v in 1..m create two vertices, one for the literal +v
  and one for -v, joined by an edge.  Vertex ids: 2*(v-1) is +v and
  2*(v-1)+1 is -v.
* For every clause create a triangle on three new vertices, one per literal
  position, and connect each triangle vertex to the literal vertex of the
  literal in that position.
* Set k = m.

A satisfying assignment yields a dominating set of size m by picking the
literal vertex that is true for each variable: it dominates its variable
gadget and every clause triangle (each clause has a true literal, and the
two other triangle vertices are adjacent to the one attached to it).

Conversely a dominating set of size at most m must contain exactly one
vertex from each variable gadget: if neither +v nor -v is chosen, then two
distinct clause vertices are needed just to dominate them, forcing the set
to have more than m vertices.  With exactly one literal vertex per variable
chosen, every clause triangle must be dominated through its attached literal
vertex, so the chosen literals satisfy every clause.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Map a 3-SAT instance to a Dominating Set instance with the same answer."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    # Variable gadgets: +v at 2*(v-1), -v at 2*(v-1)+1, joined by an edge.
    for v in range(1, num_vars + 1):
        true_vertex = 2 * (v - 1)
        false_vertex = true_vertex + 1
        edges.append([true_vertex, false_vertex])

    def literal_vertex(literal: int) -> int:
        var = abs(literal)
        base = 2 * (var - 1)
        return base if literal > 0 else base + 1

    # Clause gadgets: a triangle per clause, attached to its literal vertices.
    next_vertex = 2 * num_vars
    for clause in clauses:
        a, b, c = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for triangle_vertex, literal in zip((a, b, c), clause):
            edges.append([triangle_vertex, literal_vertex(literal)])

    return {"n": next_vertex, "edges": edges, "k": num_vars}

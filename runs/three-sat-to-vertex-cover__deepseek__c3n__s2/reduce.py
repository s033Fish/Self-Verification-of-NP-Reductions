"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For each variable v in 1..m create two vertices:
        lit_vertex(+v) = 2*(v-1)
        lit_vertex(-v) = 2*(v-1) + 1
    joined by an edge.  This edge forces at least one of the two literal
    vertices into every vertex cover.
  * For each clause create a triangle of 3 fresh vertices, one for each
    literal occurrence in the clause, and connect each triangle vertex to
    the literal vertex of its literal.  Covering a triangle needs >= 2 of
    its 3 vertices; the third one must have its edge to the literal vertex
    covered, which forces the literal to be "true".
  * k = m + 2 * (number of clauses).

A satisfying assignment yields a cover of size m + 2c (take the true
literal vertex of each variable and, for every clause, the two triangle
vertices of the false literals).  Conversely any cover of size <= m + 2c
must take exactly one vertex per variable pair and exactly two per
triangle, and the unchosen triangle vertex forces a true literal, so the
assignment is satisfying.
"""

from __future__ import annotations


def _lit_vertex(literal: int) -> int:
    """Vertex id of the literal vertex for +v / -v."""
    v = abs(literal)
    return 2 * (v - 1) + (0 if literal > 0 else 1)


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Vertex Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 2 * num_vars
    edges: list[list[int]] = []

    # Variable gadgets: one edge per variable between its two literals.
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    # Clause gadgets: a triangle per clause, with each corner linked to
    # the literal vertex of the literal it represents.
    for clause in clauses:
        base = n
        a, b, c = base, base + 1, base + 2
        n += 3
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for corner, literal in zip((a, b, c), clause):
            edges.append([corner, _lit_vertex(literal)])

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

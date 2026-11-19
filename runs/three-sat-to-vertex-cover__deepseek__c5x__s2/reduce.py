"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Standard gadget reduction:

Variables: for each variable v in 1..m create two vertices
    true(v)  = 2*(v-1)
    false(v) = 2*(v-1) + 1
joined by an edge, so every vertex cover must pick at least one of them.

Clauses: for each clause create a triangle on three new vertices, one per
literal.  A vertex cover must pick at least two vertices of a triangle.

Consistency: connect the literal vertex of +v to false(v) and the literal
vertex of -v to true(v).  Picking the literal vertex in the cover then
forces the variable gadget to pick the vertex matching a satisfying
assignment (and vice versa).

With c clauses and m variables, the budget is k = m + 2c.
"""

from __future__ import annotations

from problems import SOURCE, TARGET


def reduce(instance):
    """Map a 3-SAT instance to a Vertex Cover instance."""
    SOURCE.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    c = len(clauses)

    def true_vertex(v):
        return 2 * (v - 1)

    def false_vertex(v):
        return 2 * (v - 1) + 1

    edges = []
    # Variable gadgets: one edge per variable.
    for v in range(1, m + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    # Clause gadgets: a triangle per clause plus consistency edges.
    for ci, clause in enumerate(clauses):
        base = 2 * m + 3 * ci
        a, b, d = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, d])
        edges.append([a, d])
        for offset, literal in enumerate(clause):
            lit_vertex = base + offset
            if literal > 0:
                edges.append([lit_vertex, false_vertex(literal)])
            else:
                edges.append([lit_vertex, true_vertex(-literal)])

    n = 2 * m + 3 * c
    k = m + 2 * c
    result = {"n": n, "edges": edges, "k": k}
    TARGET.validate(result)
    return result

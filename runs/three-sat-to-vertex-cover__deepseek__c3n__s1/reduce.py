"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For each variable v in 1..m create two vertices: one meaning "v is true"
    and one meaning "v is false", joined by an edge.  Any vertex cover must
    pick at least one of the two, i.e. it "chooses" a truth value for v.
  * For each clause create a triangle on three fresh vertices, one per
    literal.  Any vertex cover must pick at least two of the three triangle
    vertices, i.e. it may leave at most one literal "uncovered" -- that
    literal must be satisfied by the chosen truth assignment.
  * Connect the triangle vertex of literal l to the variable vertex that
    makes l true (v for +v, the false-vertex for -v).  Picking the variable
    vertex then covers the edge, so the clause vertex need not be picked.

Set k = m + 2 * (#clauses).  The formula is satisfiable iff the graph has a
vertex cover of size at most k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex layout:
    #   true_vertex[v]  = 2*(v-1)      for v in 1..num_vars
    #   false_vertex[v] = 2*(v-1) + 1
    #   clause vertices follow, 3 per clause.
    def true_vertex(v: int) -> int:
        return 2 * (v - 1)

    def false_vertex(v: int) -> int:
        return 2 * (v - 1) + 1

    edges: list[list[int]] = []

    # Variable gadgets: one edge per variable.
    for v in range(1, num_vars + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    next_vertex = 2 * num_vars
    for clause in clauses:
        tri = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3
        # Triangle on the three literal vertices.
        edges.append([tri[0], tri[1]])
        edges.append([tri[1], tri[2]])
        edges.append([tri[0], tri[2]])
        # Edge from each literal vertex to the variable vertex satisfying it.
        for literal, cv in zip(clause, tri):
            if literal > 0:
                edges.append([cv, true_vertex(literal)])
            else:
                edges.append([cv, false_vertex(-literal)])

    n = next_vertex
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

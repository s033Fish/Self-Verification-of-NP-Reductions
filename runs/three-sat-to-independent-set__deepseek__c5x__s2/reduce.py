"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause create a triangle of 3 vertices, one per literal.
    Edges inside a triangle forbid picking two literals of the same clause.
  * For every pair of vertices (in different triangles) whose literals are
    complementary (v and -v), add an edge.  This forbids picking a literal
    together with its negation.
  * Set k = number of clauses.

A satisfying assignment picks, for each clause, one true literal; these
picked literals are pairwise non-adjacent (one per clause, no complementary
pair), giving an independent set of size = #clauses.  Conversely an
independent set of size #clauses must pick exactly one vertex per triangle
(triangles are cliques of size 3 and there are #clauses triangles), and the
absence of complementary edges makes the chosen literals consistently
true, yielding a satisfying assignment.

The construction is polynomial: O(#clauses^2) vertices/edges.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertex_of[(clause_index, literal_index)] = vertex id
    vertices: list[tuple[int, int]] = []  # (clause_index, literal_index)
    edges: list[list[int]] = []

    for ci, clause in enumerate(clauses):
        base = len(vertices)
        for li in range(3):
            vertices.append((ci, li))
        # triangle among the three literals of this clause
        edges.append([base + 0, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base + 0, base + 2])

    n = len(vertices)

    # complementary edges between different clauses
    for i in range(n):
        ci, li = vertices[i]
        lit_i = clauses[ci][li]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue
            lit_j = clauses[cj][lj]
            if lit_i == -lit_j:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For each variable v in 1..m create two vertices, one meaning "v is true"
    and one meaning "v is false", joined by an edge.  Any vertex cover must
    pick at least one of them.
  * For each clause create a triangle of three vertices, one per literal.
    Any vertex cover must pick at least two vertices of each triangle.
  * Connect the triangle vertex of a literal to the variable vertex that
    makes that literal FALSE (for literal +v that is the "v is false"
    vertex; for literal -v that is the "v is true" vertex).

Set k = m + 2 * (number of clauses).

A cover of size k exists iff the formula is satisfiable: the variable edges
force >= m picks and the triangles force >= 2 picks per clause, so a cover of
size k picks exactly one vertex per variable and exactly two per triangle.
The chosen variable vertices give an assignment; the connection edges force
the omitted triangle vertex of every clause to be a true literal, so every
clause is satisfied.  Conversely a satisfying assignment yields such a cover.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Map a 3-SAT instance to a Vertex Cover instance (same yes/no answer)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Variable v (1..m): true vertex 2*(v-1), false vertex 2*(v-1)+1.
    def true_vertex(v: int) -> int:
        return 2 * (v - 1)

    def false_vertex(v: int) -> int:
        return 2 * (v - 1) + 1

    edges: list[list[int]] = []

    # One edge per variable, forcing a choice of truth value.
    for v in range(1, num_vars + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    # One triangle per clause, plus a connection edge per literal.
    clause_base = 2 * num_vars
    for j, clause in enumerate(clauses):
        base = clause_base + 3 * j
        a, b, c = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for offset, literal in enumerate(clause):
            var = abs(literal)
            if literal > 0:
                # +v is false exactly when the "v is false" vertex is chosen.
                target = false_vertex(var)
            else:
                # -v is false exactly when the "v is true" vertex is chosen.
                target = true_vertex(var)
            edges.append([base + offset, target])

    n = 2 * num_vars + 3 * len(clauses)
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

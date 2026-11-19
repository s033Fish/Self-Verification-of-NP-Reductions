"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For each variable v in 1..m create two vertices: a "true" vertex and a
    "false" vertex, joined by an edge.  Any vertex cover must contain at
    least one of the two.
  * For each clause create a triangle on three new vertices, one per
    literal.  Any vertex cover must contain at least two of the three.
  * Join the triangle vertex of a literal to the variable vertex that makes
    that literal FALSE (literal +v -> false vertex of v; literal -v -> true
    vertex of v).
  * Set k = m + 2 * (number of clauses).

A cover of size k must pick exactly one vertex per variable pair (defining a
truth assignment) and exactly two vertices per clause triangle.  The omitted
triangle vertex has its cross edge covered only by the variable vertex, which
forces the corresponding literal to be true.  Hence a cover of size <= k
exists iff the formula is satisfiable.
"""

from typing import Any


def reduce(instance: Any) -> Any:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    # Variable gadgets: true vertex 2*(v-1), false vertex 2*(v-1)+1.
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    next_vertex = 2 * num_vars
    for clause in clauses:
        base = next_vertex
        next_vertex += 3
        # Triangle on the three literal vertices.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])
        # Cross edges to the variable vertex that falsifies the literal.
        for offset, literal in enumerate(clause):
            var = abs(literal)
            if literal > 0:
                # +v is false when the false vertex is chosen.
                target = 2 * (var - 1) + 1
            else:
                # -v is false when the true vertex is chosen.
                target = 2 * (var - 1)
            edges.append([base + offset, target])

    n = next_vertex
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

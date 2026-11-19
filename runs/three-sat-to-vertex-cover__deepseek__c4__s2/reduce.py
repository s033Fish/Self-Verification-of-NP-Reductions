"""Polynomial-time reduction from 3-SAT (SOURCE) to Vertex Cover (TARGET).

Standard gadget reduction:

* For every variable v in 1..m create two vertices, T(v) and F(v), joined by
  an edge.  Any vertex cover must pick at least one of them.
* For every clause create a triangle on three new vertices, one per literal.
  Any vertex cover must pick at least two of the three triangle vertices.
* Join the clause vertex of each literal to the variable vertex that makes
  that literal true (T(v) for +v, F(v) for -v).

With k = m + 2*c (c = number of clauses) a cover of size <= k exists iff the
formula is satisfiable:

  - There are m variable edges (>= 1 vertex each) and c triangles (>= 2
    vertices each), so at least m + 2c = k vertices are needed.  A cover of
    size k therefore uses exactly one vertex per variable edge and exactly two
    per triangle.
  - For each clause the one unselected triangle vertex corresponds to a
    literal whose variable vertex must be selected (to cover its linking
    edge), i.e. a true literal.  Reading off the selected variable vertices
    gives a satisfying assignment.
  - Conversely, from a satisfying assignment select the true vertex of each
    variable and, per clause, the two triangle vertices of false literals;
    the unselected vertex is a true literal whose linking edge is covered by
    the variable vertex.  This is a cover of size exactly k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Vertex Cover instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)

    n = 2 * m + 3 * c
    edges: list[list[int]] = []

    # Variable gadgets: vertices 2*(v-1) [true] and 2*(v-1)+1 [false].
    for v in range(1, m + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    def var_vertex(literal: int) -> int:
        if literal > 0:
            return 2 * (literal - 1)
        return 2 * (-literal - 1) + 1

    # Clause gadgets: a triangle of three fresh vertices, one per literal,
    # each linked to the variable vertex that makes the literal true.
    for i, clause in enumerate(clauses):
        base = 2 * m + 3 * i
        a, b, d = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, d])
        edges.append([a, d])
        for j, literal in enumerate(clause):
            edges.append([base + j, var_vertex(literal)])

    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}

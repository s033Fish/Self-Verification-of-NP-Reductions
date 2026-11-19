"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Standard gadget reduction.

For a formula with m variables and c clauses:

* Variable gadget: for each variable v, two vertices T_v and F_v joined by an
  edge.  Any vertex cover must pick at least one of them.
* Clause gadget: for each clause, a triangle on three vertices, one per
  literal.  Any vertex cover must pick at least two of the three.
* Connection: the triangle vertex for a literal is joined to the variable
  vertex that makes that literal true (T_v for +v, F_v for -v).

Set k = m + 2c.  The formula is satisfiable iff the graph has a vertex cover
of size at most m + 2c.

Vertex numbering:
  variable v (1..m): true  -> 2*(v-1), false -> 2*(v-1)+1
  clause j (0-based): triangle -> 2*m + 3*j, +1, +2
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    c = len(clauses)

    edges: list[list[int]] = []

    # Variable gadgets: one edge per variable.
    for v in range(1, m + 1):
        true_vertex = 2 * (v - 1)
        false_vertex = 2 * (v - 1) + 1
        edges.append([true_vertex, false_vertex])

    # Clause gadgets: a triangle per clause plus connections to variable
    # vertices.
    for j, clause in enumerate(clauses):
        base = 2 * m + 3 * j
        a, b, d = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, d])
        edges.append([a, d])
        for pos, literal in enumerate(clause):
            var = abs(literal)
            if literal > 0:
                var_vertex = 2 * (var - 1)      # literal true iff var is true
            else:
                var_vertex = 2 * (var - 1) + 1  # literal true iff var is false
            edges.append([base + pos, var_vertex])

    n = 2 * m + 3 * c
    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}

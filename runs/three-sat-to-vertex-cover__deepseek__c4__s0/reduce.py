"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For every variable v in 1..m create two vertices:
        true_v  = 2*(v-1)
        false_v = 2*(v-1) + 1
    joined by an edge.  Any vertex cover must pick at least one of them.
  * For every clause c = (l1, l2, l3) create a triangle of three vertices
    (one per literal).  Any vertex cover must pick at least two of them.
  * Connect the clause vertex for literal l to the variable vertex that
    makes l true:  +v -> true_v,  -v -> false_v.
  * Set k = m + 2 * (#clauses).

A cover of size <= k exists iff the formula is satisfiable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    # Variable gadgets: one edge per variable between its true/false vertex.
    for v in range(1, num_vars + 1):
        t = 2 * (v - 1)
        f = 2 * (v - 1) + 1
        edges.append([t, f])

    n = 2 * num_vars

    # Clause gadgets: a triangle per clause, with edges to variable gadgets.
    for clause in clauses:
        base = n
        n += 3
        c0, c1, c2 = base, base + 1, base + 2
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c0, c2])
        for idx, literal in enumerate(clause):
            var = abs(literal)
            true_vertex = 2 * (var - 1)
            false_vertex = 2 * (var - 1) + 1
            target = true_vertex if literal > 0 else false_vertex
            edges.append([base + idx, target])

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Standard gadget reduction:

* For every variable v (1..m) create two vertices: pos(v) = 2*(v-1) and
  neg(v) = 2*(v-1)+1, joined by an edge.  Any vertex cover must pick at
  least one of the two, and picking exactly one corresponds to assigning v
  true (pick pos) or false (pick neg).

* For every clause create a triangle on three fresh vertices, one per
  literal.  A vertex cover must pick at least two of the three triangle
  vertices.  Each literal vertex is additionally connected to the variable
  vertex that would make that literal false, so a cover that picks only two
  triangle vertices must be "paid for" by the variable vertex being on the
  other side (i.e. the literal is satisfied).

Budget k = m + 2 * (#clauses).

The formula is satisfiable iff the graph has a vertex cover of size <= k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Map a 3-SAT instance to a Vertex Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    # Variable gadgets: one edge per variable.
    for v in range(1, num_vars + 1):
        pos = 2 * (v - 1)
        neg = 2 * (v - 1) + 1
        edges.append([pos, neg])

    n = 2 * num_vars

    # Clause gadgets: a triangle per clause, plus edges to variable vertices.
    for clause in clauses:
        base = n
        n += 3
        # Triangle among the three literal vertices.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])
        for offset, literal in enumerate(clause):
            var = abs(literal)
            pos = 2 * (var - 1)
            neg = 2 * (var - 1) + 1
            if literal > 0:
                # Positive literal is falsified by v = false -> neg vertex.
                edges.append([base + offset, neg])
            else:
                # Negative literal is falsified by v = true -> pos vertex.
                edges.append([base + offset, pos])

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

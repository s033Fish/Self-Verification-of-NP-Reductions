"""Polynomial-time reduction from 3-SAT (ThreeSat) to Independent Set.

Standard gadget reduction:
  * One triangle of 3 vertices per clause (one vertex per literal).
    An independent set can contain at most one vertex per clause.
  * An edge between every pair of complementary literals (v and -v) in
    different clauses, forbidding an inconsistent choice.
  * k = number of clauses.

A satisfying assignment yields an independent set of size = #clauses by
picking one true literal per clause; conversely an independent set of size
#clauses picks exactly one literal per clause, no two complementary, so the
induced assignment satisfies every clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges: list[list[int]] = []

    # One triangle per clause: vertices 3*i, 3*i+1, 3*i+2.
    for i in range(len(clauses)):
        a, b, c = 3 * i, 3 * i + 1, 3 * i + 2
        edges.append([a, b])
        edges.append([a, c])
        edges.append([b, c])

    # Map each literal to the vertices representing it.
    occurrences: dict[int, list[int]] = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            occurrences.setdefault(literal, []).append(3 * i + j)

    # Edges between complementary literals (they are in different clauses
    # because a clause never contains both v and -v).  Process each
    # complementary pair once to avoid emitting duplicate edges.
    for literal, verts in occurrences.items():
        if literal > -literal:
            continue
        for u in verts:
            for v in occurrences.get(-literal, ()):
                edges.append([u, v])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

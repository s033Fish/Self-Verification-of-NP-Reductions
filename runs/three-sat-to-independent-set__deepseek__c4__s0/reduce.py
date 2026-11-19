"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause c_i = (l1, l2, l3) create three vertices, one for each
    literal occurrence.  Vertices are numbered 3*i, 3*i+1, 3*i+2.
  * Within each clause-triple add all three edges (a triangle), so at most
    one vertex per clause can be chosen.
  * Between any two vertices whose literals are complementary (v and -v),
    add an edge, so a chosen set cannot contain both a literal and its
    negation.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking one true literal per clause; conversely an independent set of size
#clauses picks exactly one literal per clause, consistent (no v and -v
together), and setting those literals true satisfies every clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges: list[list[int]] = []

    # literal stored per vertex
    literal_of: list[int] = []

    for i, clause in enumerate(clauses):
        base = 3 * i
        for j, lit in enumerate(clause):
            literal_of.append(lit)
        # triangle edges inside the clause
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])

    # conflict edges between complementary literals
    for u in range(n):
        for v in range(u + 1, n):
            if literal_of[u] == -literal_of[v]:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}

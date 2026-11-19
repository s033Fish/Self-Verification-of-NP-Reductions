"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause create a triangle of 3 vertices, one per literal.
  * Add an edge between any two vertices whose literals are complementary
    (i.e. v and -v).
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; these chosen
vertices form an independent set of size (#clauses).  Conversely an
independent set of size (#clauses) must pick exactly one vertex per
triangle, and the absence of complementary edges makes the chosen literals
consistent, yielding a satisfying assignment.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertex id for (clause index, literal position)
    n = 3 * len(clauses)
    edge_set: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        edge_set.add(frozenset((u, v)))

    # triangle edges within each clause
    for c in range(len(clauses)):
        base = 3 * c
        add_edge(base, base + 1)
        add_edge(base + 1, base + 2)
        add_edge(base, base + 2)

    # edges between complementary literals
    literal_vertices: dict[int, list[int]] = {}
    for c, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            literal_vertices.setdefault(lit, []).append(3 * c + pos)

    for lit, verts in literal_vertices.items():
        for u in verts:
            for v in literal_vertices.get(-lit, []):
                add_edge(u, v)

    edges = [sorted(e) for e in edge_set]
    return {"n": n, "edges": edges, "k": len(clauses)}

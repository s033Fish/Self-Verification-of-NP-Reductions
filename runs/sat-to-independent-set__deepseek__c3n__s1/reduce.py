"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard):
  * For every clause and every literal occurrence in that clause, create a
    vertex.  Occurrences are kept separate, so repeated literals in a clause
    become distinct vertices.
  * Inside a clause, connect every pair of its vertices (a clique).  This
    forces an independent set to pick at most one literal per clause.
  * For every two vertices belonging to *different* clauses whose literals
    are complementary (v and -v), add an edge.  This forbids picking both a
    literal and its negation.
  * Set k = number of clauses.

A satisfying assignment yields an independent set by picking, in each clause,
one true literal's vertex (clauses are pairwise non-conflicting).  Conversely
an independent set of size >= #clauses must pick exactly one vertex per clause,
and the chosen literals are mutually consistent, giving a satisfying
assignment.  An empty clause contributes no vertex, so the maximum independent
set is then < #clauses (answer no), matching SAT.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # vertex id -> literal it represents
    vertex_literal: list[int] = []
    # clause index -> list of vertex ids
    clause_vertices: list[list[int]] = []

    for clause in clauses:
        ids: list[int] = []
        for literal in clause:
            ids.append(len(vertex_literal))
            vertex_literal.append(literal)
        clause_vertices.append(ids)

    n = len(vertex_literal)
    edges: list[list[int]] = []
    seen: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        key = frozenset((u, v))
        if key in seen:
            return
        seen.add(key)
        edges.append([u, v])

    # Clique edges within each clause.
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Complement edges between different clauses.
    for a in range(len(clauses)):
        for b in range(a + 1, len(clauses)):
            for u in clause_vertices[a]:
                lu = vertex_literal[u]
                for v in clause_vertices[b]:
                    if lu == -vertex_literal[v]:
                        add_edge(u, v)

    return {"n": n, "edges": edges, "k": len(clauses)}

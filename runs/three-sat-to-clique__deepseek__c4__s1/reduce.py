"""Polynomial-time reduction from 3-SAT to Clique.

Standard reduction (Karp):
  * For every clause create one vertex per literal in that clause.
  * Two vertices are joined by an edge iff they come from different clauses
    and their literals are not complementary (i.e. they can be simultaneously
    true).
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; the corresponding
vertices are pairwise compatible (different clauses, no complementary pair),
so they form a clique of size = number of clauses.  Conversely a clique of
size = number of clauses must contain exactly one vertex per clause (vertices
from the same clause are never adjacent) and no complementary pair, so the
chosen literals can all be set true simultaneously, satisfying every clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # Vertex id -> (clause_index, literal)
    vertices: list[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)
    edges: list[list[int]] = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            # Same clause -> no edge (a clique can use at most one literal
            # from each clause).
            if ci == cj:
                continue
            # Complementary literals cannot both be true -> no edge.
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

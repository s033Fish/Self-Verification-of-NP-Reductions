"""Polynomial-time reduction from 3-SAT to Clique.

Construction (standard):
  * For every clause, create one vertex per literal in that clause.
  * Join two vertices by an edge iff they belong to different clauses and
    their literals are not complementary (i.e. not x and -x).
  * Set k = number of clauses.

A satisfying assignment yields a k-clique by picking one true literal per
clause.  Conversely, a k-clique must contain exactly one vertex per clause
(no edges inside a clause) and cannot contain complementary literals, so it
induces a consistent satisfying assignment.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # vertex i corresponds to (clause index, literal)
    vertices: list[tuple[int, int]] = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)
    edges: list[list[int]] = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue  # same clause: never adjacent
            if li == -lj:
                continue  # complementary literals: never adjacent
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

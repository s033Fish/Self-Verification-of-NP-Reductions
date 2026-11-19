"""Polynomial-time reduction from 3-SAT to Independent Set.

Standard reduction:
  * For every clause create a triangle of 3 vertices, one per literal.
  * For every pair of vertices in different triangles whose literals are
    complementary (v and -v), add an edge.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking, in each triangle, a vertex whose literal is true.  Conversely any
independent set of size (#clauses) picks exactly one vertex per triangle
(at most one is possible inside a triangle), and the absence of
contradiction edges makes the chosen literals simultaneously satisfiable.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    n = 3 * num_clauses
    edges: list[list[int]] = []

    # Triangle edges inside each clause gadget.
    for i in range(num_clauses):
        a, b, c = 3 * i, 3 * i + 1, 3 * i + 2
        edges.append([a, b])
        edges.append([a, c])
        edges.append([b, c])

    # Map each literal to the vertices representing it.
    occurrences: dict[int, list[int]] = defaultdict(list)
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            occurrences[literal].append(3 * i + j)

    # Contradiction edges between complementary literals.
    seen: set[frozenset[int]] = set()
    for literal, vertices in occurrences.items():
        for u in vertices:
            for v in occurrences.get(-literal, ()):
                key = frozenset((u, v))
                if key not in seen:
                    seen.add(key)
                    edges.append([u, v])

    return {"n": n, "edges": edges, "k": num_clauses}

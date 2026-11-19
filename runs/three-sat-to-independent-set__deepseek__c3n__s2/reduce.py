"""Polynomial-time reduction from 3-SAT (ThreeSat) to Independent Set.

Reduction (standard):
  * For every clause create a triangle of 3 vertices, one per literal.
  * Add an edge between every pair of vertices whose literals are
    complementary (v and -v).
  * Set k = number of clauses.

An independent set of size k must pick exactly one vertex from each
triangle (a triangle is a clique, so at most one per clause).  The
complementary-literal edges then force the chosen literals to come from
a single consistent assignment, which satisfies every clause.  Conversely
a satisfying assignment yields such an independent set by choosing one
true literal per clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []
    # vertex index -> literal it represents
    vertex_literal: list[int] = []

    for clause in clauses:
        base = len(vertex_literal)
        # Triangle: all three pairs inside the clause are adjacent.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])
        vertex_literal.extend(clause)

    # Group vertices by the literal they represent.
    by_literal: dict[int, list[int]] = {}
    for vertex, literal in enumerate(vertex_literal):
        by_literal.setdefault(literal, []).append(vertex)

    # Complementary-literal edges: complete bipartite between the
    # vertices of v and the vertices of -v.
    seen: set[frozenset[int]] = set()
    for edge in edges:
        seen.add(frozenset(edge))

    for literal, vertices in by_literal.items():
        if literal < 0:
            continue  # handle each complementary pair once, via the positive side
        for other in by_literal.get(-literal, []):
            for vertex in vertices:
                key = frozenset((vertex, other))
                if key not in seen:
                    seen.add(key)
                    edges.append([vertex, other])

    return {"n": len(vertex_literal), "edges": edges, "k": len(clauses)}

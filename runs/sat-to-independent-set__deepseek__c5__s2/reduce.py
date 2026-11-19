"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard):
  * One vertex per literal occurrence in the formula.
  * Within each clause, all vertices form a clique, so an independent set
    can pick at most one literal per clause.
  * For every pair of contradictory literals (v and -v) in different
    vertices, add an edge, so a consistent assignment is enforced.
  * k = number of clauses.

A satisfying assignment yields an independent set of size = #clauses by
picking one true literal per clause.  Conversely, any independent set of
size >= #clauses picks exactly one literal per clause with no contradictions,
giving a satisfying assignment.  An empty clause contributes no vertex, so
the target answer is no exactly when the formula is unsatisfiable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    literals: list[int] = []
    clause_vertices: list[list[int]] = []
    for clause in clauses:
        vs: list[int] = []
        for literal in clause:
            vs.append(len(literals))
            literals.append(literal)
        clause_vertices.append(vs)

    edges: set[frozenset[int]] = set()

    # Clique inside every clause.
    for vs in clause_vertices:
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                edges.add(frozenset((vs[i], vs[j])))

    # Edges between contradictory literals.
    by_literal: dict[int, list[int]] = {}
    for vertex, literal in enumerate(literals):
        by_literal.setdefault(literal, []).append(vertex)
    for literal, vertices in by_literal.items():
        opposite = by_literal.get(-literal)
        if opposite is None:
            continue
        for a in vertices:
            for b in opposite:
                edges.add(frozenset((a, b)))

    return {
        "n": len(literals),
        "edges": [sorted(edge) for edge in edges],
        "k": len(clauses),
    }

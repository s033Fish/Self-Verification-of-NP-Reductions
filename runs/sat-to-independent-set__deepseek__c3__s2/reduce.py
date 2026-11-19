"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard):
  * For every clause, create one vertex per literal occurrence in that clause,
    and connect all vertices of the same clause into a clique.  An independent
    set can therefore pick at most one literal per clause.
  * For every variable v, connect every vertex labelled v with every vertex
    labelled -v.  An independent set can therefore never pick a literal and
    its negation.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by picking
one true literal per clause.  Conversely, an independent set of size
(#clauses) picks exactly one literal per clause, and the chosen literals are
mutually consistent, so they define a satisfying assignment (variables that do
not occur may be set arbitrarily).

Edge cases:
  * No clauses  -> k = 0, always yes (matches SAT).
  * Empty clause [] -> contributes no vertex, so the maximum independent set
    is strictly smaller than k = #clauses, hence "no" (matches SAT).
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # Build the vertices: one per literal occurrence, grouped by clause.
    # vertex_literal[i] is the literal that vertex i represents.
    vertex_literal: list[int] = []
    clause_vertices: list[list[int]] = []
    for clause in clauses:
        group = []
        for literal in clause:
            group.append(len(vertex_literal))
            vertex_literal.append(literal)
        clause_vertices.append(group)

    n = len(vertex_literal)

    # Edges are collected as unordered pairs in a set to avoid duplicates
    # (e.g. a clause containing both v and -v produces the same pair twice).
    edge_set: set[frozenset[int]] = set()

    # Clique within each clause: at most one literal per clause.
    for group in clause_vertices:
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                edge_set.add(frozenset((group[i], group[j])))

    # Contradiction edges: cannot choose both v and -v.
    by_literal: dict[int, list[int]] = {}
    for vertex, literal in enumerate(vertex_literal):
        by_literal.setdefault(literal, []).append(vertex)
    for literal, vertices in by_literal.items():
        opposite = -literal
        if opposite in by_literal and literal < opposite:
            for u in vertices:
                for v in by_literal[opposite]:
                    edge_set.add(frozenset((u, v)))

    edges = [sorted(edge) for edge in edge_set]

    return {"n": n, "edges": edges, "k": len(clauses)}

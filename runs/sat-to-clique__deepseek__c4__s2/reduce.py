"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction:
  * One vertex for every literal occurrence in the formula.  A vertex
    remembers which clause it came from.
  * Two vertices are joined by an edge iff they come from different
    clauses and their literals are not complementary (i.e. not v and -v).
  * k = number of clauses.

A clique of size k must pick exactly one vertex from each clause (no two
vertices of the same clause are adjacent), and the chosen literals are
pairwise non-complementary, so they can all be set true simultaneously;
this satisfies every clause.  Conversely a satisfying assignment lets us
pick one true literal per clause, giving a k-clique.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to a Clique instance (same yes/no answer)."""
    clauses = instance["clauses"]

    # Vertex i corresponds to the i-th literal occurrence; record its clause.
    vertex_clause: list[int] = []
    vertex_literal: list[int] = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertex_clause.append(clause_index)
            vertex_literal.append(literal)

    n = len(vertex_literal)
    edges: list[list[int]] = []
    for i in range(n):
        ci = vertex_clause[i]
        li = vertex_literal[i]
        for j in range(i + 1, n):
            if vertex_clause[j] == ci:
                continue  # same clause: never adjacent
            if li == -vertex_literal[j]:
                continue  # complementary literals: cannot both be true
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

"""Polynomial-time reduction from SAT to Clique.

Reduction (standard):
  * One vertex for every literal occurrence in every clause.
  * Two vertices are joined by an edge iff they come from *different*
    clauses and their literals are not complementary (i.e. not {v, -v}).
  * k = number of clauses.

Correctness:
  (=>) Given a satisfying assignment, pick one true literal in each clause.
       The chosen vertices lie in distinct clauses and no two are
       complementary (both are true under the assignment), so they form a
       clique of size k.
  (<=) A clique of size k must use exactly one vertex per clause (vertices
       inside one clause are never adjacent, and there are k clauses).
       Assign each variable the truth value forced by the chosen literal;
       this is consistent because no two chosen literals are complementary.
       Every clause then contains a true literal, so the formula is
       satisfiable.

Edge cases:
  * No clauses -> k = 0, empty graph, answer yes (matches SAT).
  * An empty clause contributes no vertex, so no clique of size k can
    exist -> answer no (matches SAT).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to a Clique instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Build one vertex per literal occurrence, remembering its clause index.
    vertex_clause: list[int] = []
    vertex_literal: list[int] = []
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertex_clause.append(ci)
            vertex_literal.append(literal)

    n = len(vertex_literal)

    edges: list[list[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if vertex_clause[i] == vertex_clause[j]:
                continue
            # complementary literals cannot both be true
            if vertex_literal[i] == -vertex_literal[j]:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

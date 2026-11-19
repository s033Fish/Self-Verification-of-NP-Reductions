"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard reduction:
  * For every occurrence of a literal in a clause, create one vertex.
  * Join two vertices iff they come from *different* clauses and their
    literals are not complementary (i.e. not v and -v).
  * Set k = number of clauses.

A clique of size k must pick exactly one vertex per clause (no two vertices
from the same clause are adjacent), and the non-complementarity edges make
the chosen literals simultaneously satisfiable.  Hence a k-clique exists iff
the formula is satisfiable.

Edge cases line up with the Clique definition:
  * no clauses            -> n = 0, k = 0   (k <= 0 is yes)
  * an empty clause       -> that clause contributes no vertex, so the max
                             clique is smaller than k = #clauses (no)
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to a Clique instance (both plain dicts)."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its clause.
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
            # Different clauses and not contradictory literals.
            if ci != cj and li != -lj:
                edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

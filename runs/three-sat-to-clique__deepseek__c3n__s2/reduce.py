"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Standard reduction (Karp):
  * One vertex for every literal occurrence in every clause.
  * Two vertices are joined by an edge iff they come from different clauses
    and their literals are not complementary (i.e. they can be simultaneously
    true).
  * k = number of clauses.

A satisfying assignment picks one true literal per clause; those literals are
pairwise non-complementary, hence form a clique of size k.  Conversely a clique
of size k must pick exactly one vertex per clause (vertices of one clause are
mutually non-adjacent), and the chosen literals are pairwise compatible, so
setting those literals true satisfies every clause.

Edge case: a formula with no clauses is satisfiable.  Then k = 0 and the
returned graph (with any n, e.g. 0) is a yes-instance because k <= 0 is always
yes.  The construction is O((3 * #clauses)^2) time, hence polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # vertices[i] = (clause_index, literal)
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
            # Same clause: no edge (a clique uses at most one literal/clause).
            if ci == cj:
                continue
            # Complementary literals cannot both be true.
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

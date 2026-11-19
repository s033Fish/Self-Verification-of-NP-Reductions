"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Standard Karp reduction:
  * For every clause and every literal occurrence in it, create one vertex.
  * Two vertices are joined by an edge iff their literals come from
    different clauses and are not complementary (i.e. they can both be
    true simultaneously).
  * k = number of clauses.

A satisfying assignment picks one true literal per clause; those literals
are pairwise non-complementary and in different clauses, so they form a
clique of size (#clauses).  Conversely a clique of size (#clauses) must
contain exactly one vertex per clause (vertices from the same clause are
never adjacent), and the corresponding literals are pairwise consistent,
so setting a variable true whenever a positive literal is chosen (and
false whenever a negative literal is chosen) satisfies every clause.

Edge case: a formula with no clauses reduces to the empty graph with
k = 0, which is a yes-instance of Clique (k <= 0 is always yes), matching
the satisfiability of the empty formula.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, tagged with (clause index, literal).
    vertices = []  # list of (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)

    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            # Different clauses and non-complementary literals.
            if ci != cj and li != -lj:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

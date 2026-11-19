"""Polynomial-time reduction from 3-SAT to Clique.

Construction (standard):
  * For every clause c and every literal l in c, create one vertex.
    Vertices are grouped by clause; group i corresponds to clause i and
    has exactly 3 vertices.
  * Join two vertices u, v with an edge iff they come from different
    clauses and their literals are *compatible*, i.e. they are not
    complementary (never both x and -x).
  * Set k = number of clauses.

Correctness:
  (=>) Given a satisfying assignment, pick in each clause one literal that
       is true. These picks are pairwise in different clauses and cannot be
       complementary (both would be true), so they form a clique of size
       = number of clauses = k.
  (<=) Given a clique of size k = number of clauses, since vertices inside
       one clause-group are pairwise non-adjacent, the clique contains at
       most one vertex per group; with k groups it contains exactly one per
       group. Adjacency forbids complementary literals, so setting every
       chosen literal to true (and the rest arbitrarily) is consistent and
       satisfies every clause.
  Edge case: no clauses -> k = 0, empty graph, which is a yes-instance
  (k <= 0), matching the empty formula being satisfiable.

The construction uses O(#clauses) vertices and O(#clauses^2) edges, hence
runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    vertices = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)
    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

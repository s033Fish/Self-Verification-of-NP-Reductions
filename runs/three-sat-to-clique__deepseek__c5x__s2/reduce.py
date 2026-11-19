"""Polynomial-time reduction from 3-SAT (ThreeSat) to Clique.

Standard reduction:
  * For every literal occurrence in every clause, create one vertex.
    Vertex v is labelled (clause_index, literal).
  * Add an edge between two vertices iff they come from *different* clauses
    and their literals are not complementary (i.e. not l and -l).
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; the corresponding
k vertices are pairwise in different clauses and pairwise non-complementary,
hence form a clique of size k.  Conversely, any k-clique contains exactly one
vertex per clause (k vertices, no two from the same clause) and the chosen
literals are pairwise non-complementary, so setting them true satisfies every
clause.

Edge cases:
  * No clauses -> n = 0, edges = [], k = 0.  Clique with k <= 0 is yes, and an
    empty 3-SAT formula is satisfiable, so answers agree.
  * k = len(clauses) <= 3 * len(clauses) = n whenever clauses exist.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    vertices = []  # list of (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)

    # Edge between literals from different clauses that are not complementary.
    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci != cj and li != -lj:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

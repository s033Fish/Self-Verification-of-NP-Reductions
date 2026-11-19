"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (standard):
  * For every clause, and every literal occurrence in that clause, create a
    vertex.  Vertices are labelled with the literal they represent.
  * Two vertices are joined by an edge iff they come from *different* clauses
    and their literals are not complementary (i.e. not v and -v).
  * Set k = number of clauses.

Correctness:
  * If the formula is satisfiable, choose one true literal per clause.  These
    vertices lie in distinct clauses and no two of them are complementary
    (both are true), so they form a clique of size = #clauses = k.
  * If a clique of size >= k exists, it contains at most one vertex per clause
    (vertices from the same clause are never adjacent), so it contains exactly
    one vertex per clause.  The chosen literals are pairwise non-complementary,
    hence the assignment making all of them true is consistent and satisfies
    every clause.
  * An empty clause contributes no vertex, so a clique of size #clauses is
    impossible -> correctly "no".  A formula with no clauses gives k = 0,
    which is trivially "yes" for Clique.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a SAT instance to a Clique instance.

    instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
    returns:  {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    # vertex id -> (clause_index, literal)
    vertices = []
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
            # complementary literals cannot both be true
            if li == -lj:
                continue
            edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

"""Polynomial-time reduction from 3-SAT to Clique.

Construction (the standard one):
  * One vertex for every literal occurrence in every clause.
  * Two vertices are joined by an edge iff they come from *different*
    clauses and their literals are not complementary (i.e. not v and -v).
  * k = number of clauses.

A clique of size k must pick exactly one vertex from each clause (since
vertices from the same clause are never adjacent), and the pairwise
non-adjacency-free selection means no chosen literals contradict each
other, so the chosen literals extend to a satisfying assignment.  The
converse is immediate: a satisfying assignment yields one true literal
per clause, and those vertices are pairwise adjacent.

Edge case: a formula with no clauses is satisfiable (yes).  We map it to
the empty graph with k = 0, which Clique answers yes (k <= 0).
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertices are (clause_index, literal) occurrences.
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
            # Same clause: never adjacent (we need exactly one per clause).
            if ci == cj:
                continue
            # Complementary literals: never adjacent (would be inconsistent).
            if li == -lj:
                continue
            edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

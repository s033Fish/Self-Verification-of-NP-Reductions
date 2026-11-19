"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction:
  * One vertex per literal occurrence in the formula (clauses are groups).
  * Two vertices are adjacent iff they come from different clauses and their
    literals are compatible (not one the negation of the other).
  * k = number of clauses.

A clique of size >= k must contain exactly one vertex per clause (vertices in
the same clause are never adjacent), and its literals are pairwise compatible,
so it induces a satisfying assignment.  Conversely a satisfying assignment
picks one true literal per clause, giving a clique of size k.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Build one vertex per literal occurrence.
    vertices = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue  # same clause: never adjacent
            if li == -lj:
                continue  # complementary literals: incompatible
            edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

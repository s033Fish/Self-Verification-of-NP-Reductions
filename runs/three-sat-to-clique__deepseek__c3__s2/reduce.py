"""Polynomial-time reduction from 3-SAT to Clique.

Standard Karp reduction:
  * For every clause, create one vertex for each of its literals.
  * Join two vertices with an edge iff they come from different clauses and
    their literals are not complementary (not x and -x).
  * Set k = number of clauses.

A clique of size >= k must pick exactly one vertex per clause (no edges inside
a clause), and the non-complementarity condition makes the chosen literals a
consistent satisfying assignment.  Conversely any satisfying assignment picks
one true literal per clause, giving a clique of size k.
"""


def reduce(instance):
    clauses = instance["clauses"]

    # vertices[i] = (clause_index, literal)
    vertices = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)
    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci != cj and li != -lj:
                edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

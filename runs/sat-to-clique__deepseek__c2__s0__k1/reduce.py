"""Polynomial-time reduction from SAT (CNF) to Clique.

Source instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Target instance (Clique):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction:
    One vertex for every literal occurrence in every clause.
    Two vertices are adjacent iff they come from different clauses and
    their literals are not complementary (i.e. not v and -v).
    Set k to the number of clauses.

A satisfying assignment yields a clique of size k by choosing one true
literal from each clause.  Conversely, any k-clique must choose exactly
one vertex from each clause (vertices in the same clause are never
adjacent), and the absence of complementary edges means those choices
can be extended to a satisfying assignment.  An empty clause contributes
no vertex, so no clique can have size k in that case.
"""


def reduce(instance):
    """Return a Clique instance equivalent to the given SAT instance."""
    clauses = instance["clauses"]

    # vertex i corresponds to (clause index, literal)
    vertices = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)
    k = len(clauses)

    edges = []
    for i in range(n):
        clause_i, literal_i = vertices[i]
        for j in range(i + 1, n):
            clause_j, literal_j = vertices[j]
            # Two literals from the same clause cannot both be selected.
            if clause_i == clause_j:
                continue
            # Complementary literals cannot both be true.
            if literal_i == -literal_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": k}

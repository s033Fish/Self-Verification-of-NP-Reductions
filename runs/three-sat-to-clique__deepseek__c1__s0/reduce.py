"""Polynomial-time reduction from 3-SAT to Clique.

Source (ThreeSat):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are +v (variable v true) or -v (variable v false).

Target (Clique):
    {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph has a clique of at least k vertices.

Reduction:
    For every literal occurrence in every clause create a vertex, tagged
    with the clause it came from.  Join two vertices with an edge iff they
    belong to different clauses and their literals are not complementary
    (i.e. one is not the negation of the other).  Set k to the number of
    clauses.

    A clique can contain at most one vertex per clause (no intra-clause
    edges), so its size is at most the number of clauses.  A clique of
    size k therefore selects exactly one literal per clause, all pairwise
    non-complementary, and setting those literals true satisfies every
    clause.  Conversely, any satisfying assignment yields such a clique by
    choosing one true literal per clause.  Hence the target has a clique of
    at least k vertices iff the source formula is satisfiable.

    The construction uses O((number of clauses)^2) time and edges.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # Vertex i corresponds to (clause index, literal).
    vertices = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)
    edges = []
    for i in range(n):
        clause_i, lit_i = vertices[i]
        for j in range(i + 1, n):
            clause_j, lit_j = vertices[j]
            # At most one literal may be picked per clause.
            if clause_i == clause_j:
                continue
            # Complementary literals cannot both be true.
            if lit_i == -lit_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

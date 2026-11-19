"""Polynomial-time reduction from SAT to Clique.

Construction (standard):
  * For every clause i and every literal occurrence l in that clause, create
    one vertex.  Vertices are identified by their index in a flat list.
  * Join two vertices coming from *different* clauses exactly when their
    literals are not complementary (i.e. not l and -l).  Vertices belonging to
    the same clause are never joined.
  * Set k = number of clauses.

Correctness:
  * A satisfying assignment picks, for each clause, at least one true literal.
    Choosing one such literal per clause yields k vertices, one per clause,
    pairwise in different clauses and pairwise non-complementary (all are true
    simultaneously), hence a clique of size k.
  * Conversely a clique of size k must use exactly one vertex per clause
    (same-clause vertices are non-adjacent) and the chosen literals are
    pairwise non-complementary, so setting each chosen literal true (and the
    other variables arbitrarily) satisfies every clause.

Edge cases:
  * No clauses -> k = 0, and a clique of size >= 0 always exists, so yes.
  * An empty clause contributes no vertex, so n < k and the answer is no.
  * k <= 0 / k > n are handled by the target's own edge-case rules and match
    the source's yes/no answer.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Flat list of (clause_index, literal) for every literal occurrence.
    vertices = []
    for i, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((i, literal))

    n = len(vertices)
    edges = []
    for a in range(n):
        ca, la = vertices[a]
        for b in range(a + 1, n):
            cb, lb = vertices[b]
            if ca == cb:
                continue
            # Complementary literals cannot both be true.
            if la == -lb:
                continue
            edges.append([a, b])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

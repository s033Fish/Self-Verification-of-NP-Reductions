"""Polynomial-time reduction from SAT to Clique.

Construction (the standard Karp reduction):

  * For every clause C and every literal occurrence l in C, create a vertex
    labelled (clause_index, literal).
  * Join two vertices with an edge iff they come from *different* clauses and
    their literals are not complementary (i.e. one is not the negation of the
    other).
  * Set k = number of clauses.

Correctness:
  (=>) A satisfying assignment makes at least one literal true in every clause.
       Pick one true literal per clause.  Chosen vertices lie in distinct
       clauses and no two are complementary (both are true under the same
       assignment), so they form a clique of size k.
  (<=) A clique of size k must use at most one vertex per clause (same-clause
       vertices are never adjacent) and there are exactly k clauses, hence it
       uses exactly one vertex per clause.  The chosen literals are pairwise
       non-complementary, so setting each chosen literal to true is consistent
       and satisfies every clause.

Edge cases:
  * No clauses -> k = 0, empty graph -> "at least 0" clique -> yes (SAT yes).
  * An empty clause contributes no vertices; then k = #clauses exceeds the
    number of vertices, so no clique of size k exists -> no (SAT no).
  * Repeated literals / repeated clauses simply create extra vertices; the
    same-clause non-adjacency keeps at most one chosen per clause, so nothing
    breaks.
"""


def reduce(instance):
    """Reduce a SAT instance to a Clique instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex i corresponds to (clause_index, literal).
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
            if ci == cj:
                continue
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

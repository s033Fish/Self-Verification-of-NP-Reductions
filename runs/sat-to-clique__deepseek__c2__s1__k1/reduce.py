"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (standard):
  * For every clause, create one vertex per literal occurrence in that clause.
    Vertices coming from the same clause are never adjacent.
  * Two vertices from different clauses are adjacent iff their literals are
    not contradictory (i.e. not {v, -v} for the same variable).
  * Set k = number of clauses.

Correctness:
  (=>) A satisfying assignment has at least one true literal per clause.
       Choosing one such literal per clause yields k pairwise non-contradictory
       vertices, i.e. a clique of size k.
  (<=) A clique of size k must take exactly one vertex from each clause (no two
       vertices of one clause are adjacent), and its literals are pairwise
       non-contradictory. Setting those literals true gives a satisfying
       assignment (unused variables may be set arbitrarily).

Edge cases:
  * No clauses: k = 0, and a clique of size 0 always exists -> yes.
  * An empty clause contributes no vertex, so a clique can use at most
    (#clauses - 1) vertices, hence no clique of size k exists -> no.
  * Duplicate literals / tautological clauses are handled by using literal
    occurrences as vertices.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence, tagged with its clause index.
    vertices = []  # list of (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)

    def contradictory(a, b):
        return a == -b

    edges = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            # Same clause -> no edge. Different clauses -> edge unless the
            # literals contradict each other.
            if ci != cj and not contradictory(li, lj):
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

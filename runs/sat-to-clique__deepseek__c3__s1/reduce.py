"""Polynomial-time reduction from SAT to Clique.

Construction (standard):
  * For every clause C_i and every literal occurrence l in C_i, create one
    vertex.  (Repeated literals / repeated clauses simply yield more vertices.)
  * Join two vertices (i, l) and (j, l') with an edge iff they come from
    different clauses (i != j) and l and l' are not complementary
    (l != -l').  Two literals from the same clause are never adjacent.
  * Set k = number of clauses.

Why it works:
  A clique of size k must pick exactly one vertex from each clause (there are
  k clauses and no two vertices from the same clause are adjacent).  The edges
  guarantee the chosen literals are pairwise non-complementary, so setting
  each chosen literal to true (and its negation, if any, to false) is
  consistent and satisfies every clause.  Conversely, any satisfying
  assignment lets us choose one true literal per clause; those k vertices are
  pairwise adjacent, giving a clique of size k.

Edge cases:
  * No clauses: k = 0, the empty graph has a clique of size 0 -> yes.
  * An empty clause contributes no vertex, so at most (#clauses - 1) vertices
    exist and no clique of size k = #clauses is possible -> no.
"""


def reduce(instance):
    """Map a SAT instance to a Clique instance (same yes/no answer)."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence; remember its literal.
    literals = []  # vertex -> literal value
    clause_of = []  # vertex -> clause index
    for i, clause in enumerate(clauses):
        for lit in clause:
            literals.append(lit)
            clause_of.append(i)

    n = len(literals)

    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            # Must be from different clauses and non-complementary literals.
            if clause_of[u] != clause_of[v] and literals[u] != -literals[v]:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}

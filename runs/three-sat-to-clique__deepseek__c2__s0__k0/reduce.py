"""Polynomial-time reduction from 3-SAT to Clique.

Construction (standard Karp reduction):
  * For every occurrence of a literal in a clause, create one vertex.
  * Two vertices are joined by an edge iff they come from *different*
    clauses and their literals are not complementary (i.e. not v and -v).
  * Set k = number of clauses.

Why it works:
  * No edges are added between vertices of the same clause, so any clique
    contains at most one vertex per clause.  With k clauses, a clique of
    size k therefore contains exactly one vertex per clause.
  * A clique's vertices are pairwise adjacent, hence pairwise
    non-complementary, so the chosen literals are simultaneously
    satisfiable: set each chosen literal true.  Every clause then has a
    true literal, so the formula is satisfiable.
  * Conversely, if the formula is satisfiable, pick one true literal per
    clause; these are pairwise non-complementary and lie in different
    clauses, so they form a clique of size k.

Edge cases:
  * No clauses -> k = 0 and the empty graph; Clique answers yes for k <= 0,
    matching the satisfiability of the empty formula.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    literals = []
    clause_of = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            clause_of.append(clause_index)

    n = len(literals)
    k = len(clauses)

    # Edge between two literal occurrences iff they are in different clauses
    # and are not complementary.
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if clause_of[i] != clause_of[j] and literals[i] != -literals[j]:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": k}

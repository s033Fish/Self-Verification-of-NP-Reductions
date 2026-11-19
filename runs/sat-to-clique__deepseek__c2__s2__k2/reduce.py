"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Reduction (standard):
  * One vertex for every literal occurrence in the formula.  Occurrences in
    different clauses are distinct vertices, so repeated literals/clauses are
    handled naturally.
  * Join two vertices with an edge iff they come from *different* clauses and
    their literals are not complementary (i.e. not v and -v).
  * Set k = number of clauses.

Correctness:
  (=>) A satisfying assignment picks at least one true literal per clause.
       Choosing one such literal occurrence per clause yields exactly k
       vertices, one per clause.  They lie in distinct clauses, and two chosen
       literals cannot be complementary (both are true), so every pair is
       joined: a clique of size k.
  (<=) A clique of size k must contain at most one vertex per clause (no edges
       within a clause), hence exactly one per clause.  Assign each variable the
       truth value making its chosen literal true; no variable is forced both
       ways because complementary literals are never adjacent.  Every clause
       then contains a true literal, so the formula is satisfiable.

Edge cases:
  * No clauses: n = 0 and k = 0; Clique answers yes for k <= 0.  SAT is yes.
  * An empty clause contributes no vertex, so at most (number of clauses - 1)
    vertices can be chosen, which is < k; Clique answers no.  SAT is no.
"""


def reduce(instance):
    """Map a SAT instance to a Clique instance (see module docstring)."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence; remember which clause it came from.
    literals = []
    clause_of = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            clause_of.append(clause_index)

    n = len(literals)

    # Edge between occurrences from different clauses that are not complements.
    edges = []
    for i in range(n):
        li = literals[i]
        ci = clause_of[i]
        for j in range(i + 1, n):
            if ci != clause_of[j] and li != -literals[j]:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

"""Polynomial-time reduction from 3-SAT to Clique.

Standard Karp reduction:
  * For every clause and every literal occurrence in it, create one vertex.
    Clause i (0-indexed) contributes vertices 3*i, 3*i+1, 3*i+2.
  * Join two vertices with an edge iff they come from different clauses and
    their literals are not complementary (i.e. not x and -x).  Literals from
    the same clause are never joined.
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; those literals are
pairwise non-complementary and lie in distinct clauses, so they form a clique
of size k.  Conversely, a clique of size k must contain exactly one vertex per
clause (same-clause vertices are non-adjacent), and those literals are
pairwise compatible, so setting each chosen literal true satisfies the
formula.  Since at most one vertex per clause can be in a clique, the maximum
clique size is at most k, so "at least k" is equivalent to "exactly k".

Edge case: a formula with no clauses maps to n = 0, edges = [], k = 0, which
is a yes-instance of Clique (k <= 0 is always yes), matching the empty
formula being satisfiable.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Clique instance."""
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # One vertex per literal occurrence.
    n = 3 * num_clauses

    # For each vertex remember (clause_index, literal).
    vertex_literal = []
    for i, clause in enumerate(clauses):
        for literal in clause:
            vertex_literal.append((i, literal))

    edges = []
    for a in range(n):
        clause_a, lit_a = vertex_literal[a]
        for b in range(a + 1, n):
            clause_b, lit_b = vertex_literal[b]
            # Different clauses and non-contradictory literals.
            if clause_a != clause_b and lit_a != -lit_b:
                edges.append([a, b])

    return {"n": n, "edges": edges, "k": num_clauses}

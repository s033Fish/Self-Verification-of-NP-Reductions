"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction
------------
Given a CNF formula with clauses C_0, ..., C_{k-1}, build a graph whose
vertices are the literal *occurrences* in the formula: occurrence j of
clause i becomes a vertex.  Two vertices are joined by an edge exactly
when they come from different clauses and their literals are not
complementary (i.e. they can be simultaneously true).

Set the target k equal to the number of clauses.

Why it works
------------
A satisfying assignment makes one literal true in every clause, and those
chosen literals are pairwise non-complementary and lie in distinct
clauses, so they form a clique of size k.

Conversely, a clique of size k must contain exactly one vertex from each
of the k clauses (no two vertices of a clique share a clause).  Assigning
each chosen literal to true is consistent because edges forbid choosing
both v and -v, and it satisfies every clause.  Variables that are not
chosen can be assigned arbitrarily.

Edge cases
----------
* No clauses: k = 0, so the Clique instance is trivially yes, matching
  the satisfiable empty formula.
* An empty clause contributes no vertex, so any clique uses at most
  (#clauses - 1) vertices, which is < k; the instance is no, as required.
"""


def reduce(instance):
    """Return a Clique instance that is yes iff the SAT instance is yes."""
    clauses = instance["clauses"]

    clause_of = []         # clause index for each vertex
    literal_of = []        # literal for each vertex

    for i, clause in enumerate(clauses):
        for literal in clause:
            clause_of.append(i)
            literal_of.append(literal)

    n = len(literal_of)
    edges = []
    for a in range(n):
        for b in range(a + 1, n):
            if clause_of[a] == clause_of[b]:
                continue
            if literal_of[a] == -literal_of[b]:
                continue
            edges.append([a, b])

    return {"n": n, "edges": edges, "k": len(clauses)}

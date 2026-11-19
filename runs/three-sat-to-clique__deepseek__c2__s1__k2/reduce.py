"""Polynomial-time reduction from 3-SAT (ThreeSat) to Clique.

Construction (the classic Karp reduction)
-----------------------------------------
Given a 3-SAT instance {"num_vars": m, "clauses": [...]}:

* Create one vertex for every literal occurrence in every clause.  A vertex
  is identified with the pair (clause index, literal).
* Join two vertices with an edge exactly when they come from *different*
  clauses and their literals are not complementary (i.e. one is not the
  negation of the other).  Vertices inside the same clause are never joined.
* Set k = number of clauses.

Why it is correct
-----------------
If the formula is satisfiable, pick one true literal in each clause; the
corresponding vertices are pairwise non-contradictory and lie in distinct
clauses, so they form a clique of size k.

Conversely, any clique of size k must contain exactly one vertex per clause
(there are no edges within a clause and there are only k clauses), and the
literals of a clique are pairwise non-contradictory, so setting all of them
true (and the remaining variables arbitrarily) satisfies every clause.

The graph has n = total number of literal occurrences <= 3 * (#clauses)
vertices and O(n^2) edges, so the construction runs in polynomial time.
"""


def reduce(instance):
    """Return a Clique instance that is yes iff the 3-SAT instance is yes."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its clause.
    vertices = []  # list of (clause_index, literal)
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((clause_index, literal))

    n = len(vertices)

    edges = []
    for i in range(n):
        clause_i, literal_i = vertices[i]
        for j in range(i + 1, n):
            clause_j, literal_j = vertices[j]
            # Only different clauses may be adjacent.
            if clause_i == clause_j:
                continue
            # Complementary literals cannot both be true.
            if literal_i == -literal_j:
                continue
            edges.append([i, j])

    # A satisfying assignment selects exactly one literal per clause.
    k = len(clauses)

    return {"n": n, "edges": edges, "k": k}

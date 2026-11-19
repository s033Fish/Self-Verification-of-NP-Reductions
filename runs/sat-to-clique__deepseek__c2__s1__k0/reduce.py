"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (the standard Karp reduction)
------------------------------------------
Given a CNF formula with clauses C_0, ..., C_{k-1}, create one graph vertex
for every *occurrence* of a literal in a clause.  Two vertices are joined by
an edge exactly when:

  * they come from different clauses, and
  * their literals are not complementary (i.e. not ``v`` and ``-v``).

Set the Clique target parameter to ``k``, the number of clauses.

Correctness
-----------
* A satisfying assignment yields a clique of size k: pick one true literal
  from each clause.  The picked literals lie in distinct clauses, and no two
  can be complementary (both would have to be true).  Hence they are pairwise
  adjacent.
* A clique of size k picks one vertex per clause: vertices of the same clause
  are never adjacent, and there are exactly k clauses, so k vertices force
  exactly one per clause.  Pairwise non-complementarity means we can set all
  chosen literals to true simultaneously, satisfying every clause.

Edge cases
----------
* No clauses: k = 0, n = 0, so Clique answers yes (k <= 0).
* An empty clause contributes no vertex, so the maximum clique has size
  strictly below k and Clique answers no.
* Repeated literals / clauses and clauses containing both ``v`` and ``-v``
  are handled naturally: duplicate occurrences are distinct vertices in the
  same clause (never adjacent), and complementary literals are non-adjacent.

The construction uses O(L) vertices and O(L^2) edges for L total literal
occurrences, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a SAT instance to a Clique instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    Returns ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    clauses = instance["clauses"]

    # One vertex per literal occurrence, tagged with its clause index.
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
            # Edge iff different clauses and literals are not complementary.
            if clause_i != clause_j and literal_i != -literal_j:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

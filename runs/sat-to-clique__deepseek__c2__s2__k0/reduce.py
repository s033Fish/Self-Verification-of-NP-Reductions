"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction
-----------------------
Given a CNF formula with clauses C_0, ..., C_{k-1}:

* Create one vertex for every literal *occurrence* in every clause.  A vertex
  remembers which clause it came from and which literal it represents.
* Join two vertices with an edge exactly when
    - they come from two *different* clauses, and
    - their literals are not complementary (not ``v`` and ``-v``).
  Vertices from the same clause are never adjacent, so a clique contains at
  most one vertex per clause.
* Set ``k`` to the number of clauses.

Correctness
-----------
If the formula is satisfiable, pick in each clause one true literal and take
the corresponding vertices.  They lie in distinct clauses and, being all true
under one assignment, no two are complementary, so they form a clique of size
``k``.

Conversely, any clique has at most one vertex per clause, so a clique of size
``k`` selects exactly one vertex per clause.  Its literals are pairwise
non-complementary, hence the assignment that sets every selected literal true
is consistent and satisfies every clause.  Thus a clique of size ``k`` exists
iff the formula is satisfiable.

Edge cases
----------
* No clauses: ``k = 0`` and the empty graph is returned; Clique answers yes
  because ``k <= 0``.
* An empty clause ``[]`` contributes no vertex, so no clique can reach size
  ``k`` (a clique uses at most one vertex per clause); Clique answers no.
* Repeated literals, clauses containing both ``v`` and ``-v``, duplicate
  clauses, and unused variables are all handled by the construction above.
"""

from itertools import combinations


def reduce(instance):
    """Map a SAT instance to a Clique instance with the same yes/no answer."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, tagged with its clause index and the
    # literal it stands for.
    vertex_clause = []
    vertex_literal = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertex_clause.append(clause_index)
            vertex_literal.append(literal)

    n = len(vertex_literal)

    # Add an edge between every pair of vertices from different clauses whose
    # literals are not complementary.  Iterating over unordered pairs adds each
    # edge exactly once, so there are no duplicates.
    edges = []
    for i, j in combinations(range(n), 2):
        if vertex_clause[i] == vertex_clause[j]:
            continue
        if vertex_literal[i] == -vertex_literal[j]:
            continue
        edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}

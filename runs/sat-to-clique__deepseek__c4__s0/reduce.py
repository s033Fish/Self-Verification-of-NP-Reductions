"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (the classic Karp reduction)
-----------------------------------------
Given a CNF formula with clauses C_1, ..., C_k, build a graph G:

  * One vertex for every literal *occurrence* in the formula.  Occurrences
    are kept distinct, so a literal repeated inside a clause, or the same
    literal appearing in several clauses, yields several vertices.
  * Join two vertices with an edge iff they come from *different* clauses
    and their literals are *not* contradictory (i.e. they are not v and -v
    for the same variable).

Set k = number of clauses.

Correctness
-----------
If the formula is satisfiable, pick one true literal in each clause.  These
k occurrences lie in k distinct clauses, and no two of them are
contradictory (both are true under the satisfying assignment), so they form
a clique of size k.

Conversely, any clique contains at most one vertex per clause (vertices of
the same clause are never adjacent), so a clique of size >= k has exactly
one vertex per clause.  Setting each chosen literal to true is consistent
because adjacent vertices are non-contradictory; hence every clause is
satisfied.

Edge cases
----------
  * No clauses: k = 0, and a clique of size >= 0 always exists -> yes.
  * An empty clause contributes no vertices, so the graph has fewer than k
    vertices and no clique of size k exists -> no (correct, an empty clause
    is unsatisfiable).
  * num_vars = 0: every clause must be empty, handled as above.

The construction is clearly polynomial: the graph has one vertex per literal
occurrence and one edge per non-contradictory pair of occurrences.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a SAT instance to a Clique instance.

    Input : {"num_vars": m, "clauses": [[literal, ...], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    # vertex -> literal it represents
    literals = []
    # vertex -> index of the clause it belongs to
    clause_of = []

    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            clause_of.append(clause_index)

    n = len(literals)

    edges = []
    for u in range(n):
        lu = literals[u]
        cu = clause_of[u]
        for v in range(u + 1, n):
            # Vertices from the same clause are never adjacent.
            if clause_of[v] == cu:
                continue
            lv = literals[v]
            # Contradictory literals (v and -v) are never adjacent.
            if lu == -lv:
                continue
            edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}

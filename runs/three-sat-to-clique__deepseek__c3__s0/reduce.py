"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Standard Karp reduction:
  * For every clause and every literal in it, create one vertex.  Vertices of
    clause i are grouped together; a clique may contain at most one vertex per
    group because vertices inside a group are never adjacent.
  * Join two vertices from *different* clauses exactly when their literals are
    compatible, i.e. they are not complementary (x and -x).  A set of literals
    with no complementary pair is simultaneously satisfiable.
  * Set k = number of clauses.

A satisfying assignment selects one true literal per clause, giving a clique of
size k.  Conversely, any clique of size k picks one vertex per clause with no
complementary pair, and the corresponding literals can all be made true at
once, satisfying every clause.  Since a clique has at most one vertex per
clause, the maximum clique size is exactly k, so "at least k" matches.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Clique instance (same yes/no answer)."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence: vertex 3*i + j for clause i, literal j.
    n = 3 * len(clauses)

    # Index -> literal value, used to test compatibility.
    literal_of = []
    for clause in clauses:
        for literal in clause:
            literal_of.append(literal)

    edges = []
    for u in range(n):
        clause_u, _ = divmod(u, 3)
        lit_u = literal_of[u]
        for v in range(u + 1, n):
            clause_v, _ = divmod(v, 3)
            if clause_u == clause_v:
                # Same clause: never adjacent.
                continue
            if lit_u == -literal_of[v]:
                # Complementary literals: cannot both be true.
                continue
            edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}

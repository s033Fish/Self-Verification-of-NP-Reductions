"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard reduction (Karp):
  * For every clause and every literal occurrence in that clause, create one
    vertex.  Record (clause_index, literal) for each vertex.
  * Join two vertices with an edge iff they come from *different* clauses and
    their literals are not complementary (i.e. not x and -x).
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; the corresponding
vertices are pairwise in different clauses and non-contradictory, hence form a
clique of size k.  Conversely, a clique of size k must contain exactly one
vertex per clause (same-clause vertices are never adjacent), and the chosen
literals are pairwise consistent, so setting each chosen literal true yields a
satisfying assignment.
"""


def reduce(instance):
    """Reduce a SAT instance to a Clique instance.

    Input : {"num_vars": m, "clauses": [[literal, ...], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its clause and literal.
    vertex_clause = []   # clause index of each vertex
    vertex_literal = []  # literal value of each vertex
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertex_clause.append(ci)
            vertex_literal.append(literal)

    n = len(vertex_literal)

    # Edges between vertices in different clauses whose literals are compatible.
    edges = []
    for i in range(n):
        ci = vertex_clause[i]
        li = vertex_literal[i]
        for j in range(i + 1, n):
            if vertex_clause[j] == ci:
                continue
            if vertex_literal[j] == -li:
                continue
            edges.append([i, j])

    # Need one vertex per clause, so k = number of clauses.
    k = len(clauses)

    return {"n": n, "edges": edges, "k": k}

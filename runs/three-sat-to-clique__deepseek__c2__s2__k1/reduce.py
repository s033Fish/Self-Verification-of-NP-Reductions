"""Polynomial-time reduction from 3-SAT to Clique.

Given a 3-SAT instance with m variables and c clauses, build a graph with one
vertex per literal occurrence: vertex (i, j) represents the j-th literal of
clause i.  Join two vertices with an edge exactly when they come from
different clauses and their literals are compatible (i.e. they are not
complements of one another, so they can be simultaneously true).

A satisfying assignment selects at least one true literal per clause, and any
two selected literals are compatible, giving a clique of size c.  Conversely a
clique of size c must use exactly one vertex from each of the c clauses
(vertices in the same clause are never adjacent), and those literals can all
be set true simultaneously, satisfying every clause.

Hence the formula is satisfiable iff the graph has a clique of size >= c, so
we set k = c.  For a formula with no clauses the graph is empty and k = 0,
which Clique reports as yes (matching the empty formula being satisfiable).
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence, in clause order.
    vertices = []  # (clause_index, literal)
    for i, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((i, literal))

    n = len(vertices)

    edges = []
    for a in range(n):
        ca, la = vertices[a]
        for b in range(a + 1, n):
            cb, lb = vertices[b]
            # Same clause: literals cannot both be chosen (no edge).
            if ca == cb:
                continue
            # Complementary literals can never both be true (no edge).
            if la == -lb:
                continue
            edges.append([a, b])

    return {"n": n, "edges": edges, "k": len(clauses)}

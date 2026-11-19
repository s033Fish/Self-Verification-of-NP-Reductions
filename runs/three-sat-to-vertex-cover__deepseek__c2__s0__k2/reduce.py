"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):

  * For every variable v in 1..m create two vertices, one representing the
    literal +v (v is true) and one representing -v (v is false), joined by an
    edge.  Any vertex cover must contain at least one of the two, and a cover of
    size m (the budget we allow) must contain exactly one.

  * For every clause create a triangle on three new vertices, one per literal.
    Any vertex cover must contain at least two of the three triangle vertices,
    and a cover of size 2 per clause must contain exactly two.

  * For every clause literal, add an edge from that clause's literal vertex to
    the variable vertex representing the same literal.

  * Set k = m + 2 * (number of clauses).

If the formula is satisfiable, pick the variable vertex matching each variable's
truth value (m vertices) and, in every clause, pick two vertices whose literals
are false (possible because at least one literal is true).  This covers every
edge with exactly m + 2*C vertices.

Conversely, any vertex cover of size at most m + 2*C must contain exactly one
vertex per variable gadget and exactly two per clause triangle.  The one
uncovered triangle vertex per clause has its edge to the variable gadget covered
by the variable vertex, which therefore represents a true literal of that
clause; hence the assignment is satisfying.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Vertex Cover instance.

    Input:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex layout:
    #   variable v (1..m):  +v -> v - 1        (true)
    #                       -v -> num_vars + v - 1 (false)
    #   clause i:           triangle at 2*num_vars + 3*i + {0,1,2}
    def true_vertex(v):
        return v - 1

    def false_vertex(v):
        return num_vars + v - 1

    def literal_vertex(literal):
        if literal > 0:
            return true_vertex(literal)
        return false_vertex(-literal)

    edges = []

    # Variable gadgets: one edge per variable.
    for v in range(1, num_vars + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    # Clause gadgets.
    base = 2 * num_vars
    for i, clause in enumerate(clauses):
        a, b, c = base + 3 * i, base + 3 * i + 1, base + 3 * i + 2
        # Triangle.
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        # Edges from each literal vertex to its variable vertex.
        for offset, literal in enumerate(clause):
            edges.append([base + 3 * i + offset, literal_vertex(literal)])

    n = 2 * num_vars + 3 * len(clauses)
    k = num_vars + 2 * len(clauses)

    return {"n": n, "edges": edges, "k": k}

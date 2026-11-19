"""Polynomial-time reduction from 3-SAT (SOURCE) to Vertex Cover (TARGET).

Construction (standard):

  * For every variable v in 1..m create two vertices:
        pos(v) = 2*(v-1)      (literal +v)
        neg(v) = 2*(v-1) + 1  (literal -v)
    and the edge [pos(v), neg(v)].  Any vertex cover must contain at least
    one of the two, i.e. at least m vertices in total for these "variable
    edges".

  * For every clause i create a triangle of three new vertices, one per
    literal of the clause.  A vertex cover must contain at least two of the
    three, i.e. at least 2*C vertices for C clauses.

  * For every literal l occurring in a clause, connect the clause's literal
    vertex to the variable vertex that represents the *negation* of l:
        l = +v  ->  neg(v)
        l = -v  ->  pos(v)

  * Set k = m + 2*C.

Correctness sketch:
  (=>) Given a satisfying assignment, choose for each variable the vertex
  corresponding to its FALSE value, and for each clause choose two of the
  three literal vertices so that every literal that is false under the
  assignment gets its clause vertex chosen.  A clause has at most two false
  literals, so two clause vertices suffice.  Every cross edge from a clause
  vertex for a true literal is covered by the chosen variable vertex (the
  negation of a true literal is false).  Total size m + 2*C.

  (<=) A cover of size at most m + 2*C must use exactly one vertex per
  variable edge and exactly two per clause triangle (these edges are
  disjoint).  Read the assignment off as: variable v is TRUE iff neg(v) is
  chosen.  If some clause had all three literals false, then for each of its
  three literals the negation vertex is the TRUE value and is not chosen, so
  all three cross edges would require their clause vertices, contradicting
  that only two clause vertices are chosen.  Hence every clause has a true
  literal.

The construction uses 2*m + 3*C vertices and 3*m + 3*C edges, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Vertex Cover instance.

    Input:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 2 * num_vars + 3 * len(clauses)
    edges = []

    # Variable edges: pos(v) = 2*(v-1), neg(v) = 2*(v-1) + 1.
    for v in range(1, num_vars + 1):
        pos = 2 * (v - 1)
        neg = pos + 1
        edges.append([pos, neg])

    # Clause triangles and cross edges to the negation of each literal.
    for i, clause in enumerate(clauses):
        base = 2 * num_vars + 3 * i
        a, b, c = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

        for offset, literal in enumerate(clause):
            clause_vertex = base + offset
            var = abs(literal)
            pos = 2 * (var - 1)
            neg = pos + 1
            # Connect to the variable vertex making the literal FALSE.
            if literal > 0:
                negation_vertex = neg
            else:
                negation_vertex = pos
            edges.append([clause_vertex, negation_vertex])

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

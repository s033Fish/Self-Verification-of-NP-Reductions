"""Polynomial-time reduction from 3-SAT (ThreeSat) to Vertex Cover.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...], "k": k}

Construction (standard literal/clause gadget reduction):

  * For every variable v in 1..m create two vertices, one for the literal
    +v and one for the literal -v, joined by an edge.  Any vertex cover
    must pick at least one of the two, and picking one can be read as the
    truth value assigned to v.
  * For every clause create a triangle on three fresh vertices, one per
    literal of the clause.  Any vertex cover must pick at least two of the
    three triangle vertices.
  * Connect the triangle vertex of each clause literal to the variable
    vertex representing that same literal.  This forces the truth value
    chosen for the variable to agree with the clause literal whenever the
    clause's triangle leaves that literal vertex uncovered.

Let C be the number of clauses.  Set k = m + 2*C.  A satisfying assignment
yields a cover of exactly that size (one variable vertex per pair plus the
two non-satisfied literals of every triangle), and conversely any cover of
size at most m + 2*C must take exactly one vertex per variable pair and
exactly two per clause triangle, which forces every clause to contain a
true literal.  Hence the target is yes iff the source is satisfiable.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadget: one edge per variable, between its +v and -v vertices.
    #   +v -> 2*(v-1),  -v -> 2*(v-1) + 1
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    def literal_vertex(literal):
        v = abs(literal)
        base = 2 * (v - 1)
        return base if literal > 0 else base + 1

    # Clause gadgets: a triangle per clause, plus consistency edges.
    base = 2 * num_vars
    for clause in clauses:
        a, b, c = base, base + 1, base + 2
        # Triangle edges.
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        # Consistency edges from clause literal vertices to variable vertices.
        for offset, literal in enumerate(clause):
            edges.append([base + offset, literal_vertex(literal)])
        base += 3

    n = base  # 2*num_vars + 3*len(clauses)
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

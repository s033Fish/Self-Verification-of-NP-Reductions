"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard "variable gadget + clause gadget"):

* For every variable v in 1..m create two vertices, T_v and F_v, joined by
  an edge.  Any vertex cover must contain at least one of them.
* For every clause create a triangle on three fresh vertices, one per
  literal.  Any vertex cover must contain at least two of the three.
* Connect the clause vertex for literal +v to F_v and the clause vertex for
  literal -v to T_v (the variable vertex that would make the literal false).

Set k = m + 2 * (#clauses).  A satisfying assignment selects, for each
variable, the vertex for the chosen truth value (m vertices), and for each
clause selects the two vertices whose literals are false (2 per clause,
possible because at least one literal is true).  Conversely any cover of size
<= m + 2c must take exactly one vertex per variable gadget and exactly two
per clause triangle; the unpicked clause vertex is a true literal, so the
corresponding assignment satisfies every clause.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: variable v (1-based) -> vertices 2*(v-1) [true] and
    # 2*(v-1)+1 [false].
    def true_vertex(v):
        return 2 * (v - 1)

    def false_vertex(v):
        return 2 * (v - 1) + 1

    for v in range(1, num_vars + 1):
        edges.append([true_vertex(v), false_vertex(v)])

    base = 2 * num_vars
    for i, clause in enumerate(clauses):
        c0 = base + 3 * i
        c1 = c0 + 1
        c2 = c0 + 2
        # Triangle over the three literal vertices.
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c0, c2])
        for j, literal in enumerate(clause):
            clause_vertex = base + 3 * i + j
            if literal > 0:
                # +v is true: connect to the false vertex of v.
                edges.append([clause_vertex, false_vertex(literal)])
            else:
                # -v is true: connect to the true vertex of v.
                edges.append([clause_vertex, true_vertex(-literal)])

    n = 2 * num_vars + 3 * len(clauses)
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

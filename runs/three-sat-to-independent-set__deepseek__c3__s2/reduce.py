"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause create one vertex per literal (3 vertices), and add the
    three edges of a triangle among them.  An independent set can therefore
    contain at most one literal from each clause.
  * For every variable v and every pair of vertices carrying literals v and
    -v, add an edge.  An independent set can therefore never contain two
    contradictory literals.
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking one true literal per clause.  Conversely, an independent set of size
#clauses must pick exactly one literal from each clause triangle, and the
consistency edges guarantee the chosen literals agree on every variable, so
they define a satisfying assignment.  With no clauses k = 0, which is a yes
instance, matching the empty (satisfiable) formula.
"""


def reduce(instance):
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges = []

    # Triangle inside each clause: at most one literal per clause.
    for i in range(len(clauses)):
        base = 3 * i
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    # Consistency edges: never pick both v and -v.
    # vertex_of[literal] = list of vertices carrying that literal.
    vertex_of = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            vertex_of.setdefault(literal, []).append(3 * i + j)

    for literal, verts in vertex_of.items():
        if literal < 0:
            continue
        opposite = vertex_of.get(-literal)
        if not opposite:
            continue
        for u in verts:
            for v in opposite:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}

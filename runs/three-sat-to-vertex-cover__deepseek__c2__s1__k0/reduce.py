"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Construction (standard):
  * For every variable v in 1..m create two vertices, ``v_true`` and
    ``v_false``, joined by an edge.  A vertex cover must pick at least one of
    them; picking exactly one encodes an assignment.
  * For every clause create a triangle on three fresh vertices, one per
    literal.  A vertex cover must pick at least two vertices of each triangle.
  * Join the triangle vertex of a literal to the variable vertex that makes
    that literal true (``+v`` -> ``v_true``, ``-v`` -> ``v_false``).
  * Set k = m + 2 * (number of clauses).

A satisfying assignment picks the true variable vertex of each pair (m) and,
for every clause, the two triangle vertices other than a satisfied literal
(2 per clause), giving a cover of size k.  Conversely any cover of size k must
pick exactly one vertex per variable pair and exactly two per triangle, and the
chosen variable vertices yield a satisfying assignment.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex ids: variable v (1-based) -> 2*(v-1) for true, 2*(v-1)+1 for false.
    def var_vertex(v, positive):
        base = 2 * (v - 1)
        return base if positive else base + 1

    n = 2 * num_vars + 3 * len(clauses)
    edges = []

    # Variable gadgets: one edge per variable.
    for v in range(1, num_vars + 1):
        edges.append([var_vertex(v, True), var_vertex(v, False)])

    # Clause gadgets: a triangle per clause plus connection edges.
    for i, clause in enumerate(clauses):
        tri = [2 * num_vars + 3 * i, 2 * num_vars + 3 * i + 1, 2 * num_vars + 3 * i + 2]
        edges.append([tri[0], tri[1]])
        edges.append([tri[1], tri[2]])
        edges.append([tri[0], tri[2]])
        for vertex, literal in zip(tri, clause):
            edges.append([vertex, var_vertex(abs(literal), literal > 0)])

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

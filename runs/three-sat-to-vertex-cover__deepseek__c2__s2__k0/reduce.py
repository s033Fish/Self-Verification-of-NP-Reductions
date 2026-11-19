"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Given a 3-CNF formula with m variables and c clauses, build a graph:

  * For each variable v in 1..m, a "variable gadget": two vertices
      pos(v) = 2*(v-1)        representing literal  +v
      neg(v) = 2*(v-1) + 1    representing literal  -v
    joined by an edge.  Any vertex cover must contain at least one of them.

  * For each clause i (0-based), a "clause gadget": three new vertices
      clause_base(i) + 0, + 1, + 2
    forming a triangle.  Any vertex cover must contain at least two of them.
    Each of the three vertices is connected to the variable-gadget vertex
    for the corresponding literal occurrence.

Set k = m + 2*c.  A satisfying assignment yields a cover of size m + 2c by
taking the true literal vertex of each variable gadget and exactly two
vertices from each clause triangle (omitting one whose literal is true).
Conversely, a cover of size at most m + 2c must take exactly one vertex per
variable gadget and exactly two per clause triangle; the omitted triangle
vertex must be adjacent to a chosen literal vertex, which makes that literal
true, so the induced assignment satisfies every clause.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Vertex Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: one edge per variable, forcing a truth choice.
    for v in range(1, num_vars + 1):
        pos = 2 * (v - 1)
        neg = pos + 1
        edges.append([pos, neg])

    def literal_vertex(literal):
        v = abs(literal)
        base = 2 * (v - 1)
        return base if literal > 0 else base + 1

    # Clause gadgets: a triangle per clause, plus links to literal vertices.
    clause_vertex_count = 3 * len(clauses)
    for index, clause in enumerate(clauses):
        base = 2 * num_vars + 3 * index
        a, b, c = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for offset, literal in enumerate(clause):
            edges.append([base + offset, literal_vertex(literal)])

    n = 2 * num_vars + clause_vertex_count
    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

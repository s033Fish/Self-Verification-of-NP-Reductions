"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Standard gadget reduction:

* For every variable v in 1..m create two vertices, t_v and f_v, joined by
  an edge.  A vertex cover must pick at least one of them; with the budget
  below it picks exactly one, encoding the truth value of v.
* For every clause create a triangle on three fresh vertices.  Each triangle
  vertex is joined to the gadget vertex of the corresponding literal.  A
  triangle needs at least two of its vertices in any vertex cover, and the
  third (unpicked) vertex is the literal that the cover "claims" to satisfy.

With c clauses the budget is k = m + 2c.  The m variable edges are pairwise
disjoint and the c triangles are edge-disjoint from everything else, so any
cover needs at least m + 2c vertices.  Covers of that size correspond exactly
to satisfying assignments, hence the answer is preserved.

The construction is linear in the size of the formula, so it runs in
polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: vertex 2*(v-1) means "v is true",
    # vertex 2*(v-1)+1 means "v is false".
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    def literal_vertex(literal):
        base = 2 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    n = 2 * num_vars
    for clause in clauses:
        a, b, c = n, n + 1, n + 2
        # Triangle for the clause.
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        # Connect the triangle to the literal gadgets.
        for vertex, literal in zip((a, b, c), clause):
            edges.append([vertex, literal_vertex(literal)])
        n += 3

    k = num_vars + 2 * len(clauses)
    return {"n": n, "edges": edges, "k": k}

"""Polynomial-time reduction from 3-SAT to Dominating Set.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
For every variable v in 1..m create a triangle on three vertices:

    x_v   (literal  v is true)
    n_v   (literal -v is true)
    d_v   (a private dummy)

with all three edges present.  Any dominating set must contain at least one
vertex of each triangle: otherwise d_v has no neighbour in the set.  One
vertex of the triangle dominates the whole triangle.

For every clause j create one vertex c_j and connect it to the literal
vertex of each of its three literals (x_v for +v, n_v for -v).

Set k = m.

Correctness
-----------
If the formula is satisfiable, pick for each variable the vertex of its true
literal.  These m vertices dominate every triangle, and because every clause
has a true literal, every clause vertex is adjacent to a chosen vertex.

Conversely, let D be a dominating set with |D| <= m.  Each of the m variable
triangles must contain a vertex of D, so |D| = m, D has exactly one vertex
per triangle, and D contains no clause vertex.  Every clause vertex must
therefore be adjacent to a vertex of D, i.e. to a chosen literal vertex.
Reading the chosen literal of each triangle as the value of that variable
(arbitrary when d_v is chosen) gives a satisfying assignment.

Hence the formula is satisfiable iff the graph has a dominating set of size
at most m.  The construction uses 3m + c vertices and 3m + 3c edges, so it
runs in polynomial time.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)

    n = 3 * m + c
    edges = []

    # Variable gadgets: triangles {x_v, n_v, d_v}.
    for v in range(1, m + 1):
        base = 3 * (v - 1)
        x = base
        nx = base + 1
        d = base + 2
        edges.append([x, nx])
        edges.append([x, d])
        edges.append([nx, d])

    # Clause gadgets: one vertex per clause, joined to its literal vertices.
    for j, clause in enumerate(clauses):
        clause_vertex = 3 * m + j
        for literal in clause:
            var = abs(literal)
            base = 3 * (var - 1)
            literal_vertex = base if literal > 0 else base + 1
            edges.append([clause_vertex, literal_vertex])

    return {"n": n, "edges": edges, "k": m}

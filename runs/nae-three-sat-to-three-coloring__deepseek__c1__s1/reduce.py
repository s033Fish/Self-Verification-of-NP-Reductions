"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...]}

Construction
------------
Colours are {0, 1, 2}.  A special base vertex 0 is adjacent to every
literal vertex, so literal vertices can only receive colours 1 or 2.

Variable gadget (for variable v, 1 <= v <= m):
    pos_v = 2*v - 1   (literal +v)
    neg_v = 2*v       (literal -v)
    edges: (base, pos_v), (base, neg_v), (pos_v, neg_v)
Because both are adjacent to the base they use colours {1, 2}; being
adjacent to each other forces them to differ.  Thus exactly one is
colour 1 (interpreted as "true") and the other colour 2 ("false").

Clause gadget (for a clause (l1, l2, l3)):
    add a triangle a, b, c (three new mutually adjacent vertices) and
    connect a--l1, b--l2, c--l3, where l_i is the vertex for that literal.
A triangle needs three distinct colours.  If all three literal vertices
share one colour, then a, b, c must each avoid it and hence lie in the
other two colours, which cannot be pairwise distinct -> not colourable.
If the literals are not all equal, both colours 1 and 2 occur and the
triangle can be coloured (up to relabelling, pattern (1,2,2) is coloured
(2,0,1)) -> colourable.  Hence the gadget is 3-colourable exactly when
the clause is not-all-equal.

The graph is 3-colourable iff the formula has a satisfying NAE
assignment.  The construction uses O(m + k) vertices and edges, where k
is the number of clauses, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    base = 0

    def pos_vertex(v):
        return 2 * v - 1

    def neg_vertex(v):
        return 2 * v

    n = 1 + 2 * m + 3 * len(clauses)
    edges = []

    # Base vertex adjacent to every literal vertex, plus variable gadgets.
    for v in range(1, m + 1):
        p = pos_vertex(v)
        q = neg_vertex(v)
        edges.append([base, p])
        edges.append([base, q])
        edges.append([p, q])

    # Clause gadgets.
    next_vertex = 1 + 2 * m
    for clause in clauses:
        a = next_vertex
        b = next_vertex + 1
        c = next_vertex + 2
        next_vertex += 3

        # Triangle a, b, c.
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

        # Connect each triangle vertex to its literal vertex.
        for literal, triangle_vertex in zip(clause, (a, b, c)):
            v = abs(literal)
            literal_vertex = pos_vertex(v) if literal > 0 else neg_vertex(v)
            edges.append([triangle_vertex, literal_vertex])

    return {"n": n, "edges": edges}

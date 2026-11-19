"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance (NAE-3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Construction
------------
Use three "palette" vertices 0, 1, 2 forming a triangle.  Think of vertex 0
as a fixed base colour and 1/2 as the two truth colours.

For every variable v in 1..m create two literal vertices

    pos(v) = 3 + 2*(v-1)
    neg(v) = 3 + 2*(v-1) + 1

Both are joined to vertex 0 and to each other.  Hence each of them is
coloured 1 or 2 and they receive different colours: one means "v true",
the other means "v false".

For every clause (l1, l2, l3) create three fresh vertices u, v, w forming a
triangle, and join u to lit(l1), v to lit(l2), w to lit(l3), where lit(l)
is the literal vertex representing l.

Correctness
-----------
If the literals of a clause all have the same colour c (in {1,2}), then
u, v, w must each avoid c, so they can only use the two remaining colours,
which is impossible for a triangle.  Conversely, if the literals are not all
equal, at least one has colour 1 and one has colour 2; one can check that
u, v, w can always be assigned the three distinct colours while avoiding
their respective literals' colours.  Thus each clause gadget is colourtable
exactly when its clause is not-all-equal, and the whole graph is
3-colourable exactly when the formula is NAE-satisfiable.

The construction uses 3 + 2*m + 3*C vertices and O(m + C) edges for C
clauses, so it runs in polynomial time.
"""


def reduce(instance):
    """Return a 3-Coloring instance equivalent to the NAE-3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    seen = set()

    def add_edge(a, b):
        if a > b:
            a, b = b, a
        key = (a, b)
        if key not in seen:
            seen.add(key)
            edges.append([a, b])

    # Palette triangle: vertices 0, 1, 2.
    add_edge(0, 1)
    add_edge(1, 2)
    add_edge(0, 2)

    def lit_vertex(literal):
        var = abs(literal)
        base = 3 + 2 * (var - 1)
        return base if literal > 0 else base + 1

    # Literal vertices: one pair per variable.
    for var in range(1, m + 1):
        pos = 3 + 2 * (var - 1)
        neg = pos + 1
        add_edge(0, pos)
        add_edge(0, neg)
        add_edge(pos, neg)

    # Clause gadgets.
    next_vertex = 3 + 2 * m
    for clause in clauses:
        u = next_vertex
        v = next_vertex + 1
        w = next_vertex + 2
        next_vertex += 3

        add_edge(u, v)
        add_edge(v, w)
        add_edge(u, w)

        add_edge(u, lit_vertex(clause[0]))
        add_edge(v, lit_vertex(clause[1]))
        add_edge(w, lit_vertex(clause[2]))

    return {"n": next_vertex, "edges": edges}

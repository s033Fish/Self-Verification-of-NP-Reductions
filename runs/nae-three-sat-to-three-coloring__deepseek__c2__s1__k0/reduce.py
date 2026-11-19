"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance (NAE-3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Construction
------------
Use three base vertices forming a triangle.  Call their colours T, F and B
(B is a "base" colour).  For every variable v create two vertices, one for
the positive literal +v and one for the negative literal -v, joined to each
other and both joined to B.  Hence +v and -v must receive the two colours
T and F, in opposite ways.

For every clause (x, y, z) create a fresh triangle a, b, c and join a to the
vertex of x, b to the vertex of y and c to the vertex of z.  The three
triangle vertices must get pairwise different colours.

* If x, y, z all have the same colour (all T or all F), then a, b, c may
  not use that colour, so they are restricted to the other two colours,
  which is impossible for a triangle.
* Otherwise the clause has at least one T literal and at least one F
  literal.  Colour the triangle vertex attached to a T literal with F, the
  one attached to an F literal with T, and the remaining triangle vertex
  with B; all constraints are satisfied.

Therefore the graph is 3-colourable iff the NAE-3-SAT instance is a yes
instance.  The construction is linear in the input size.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    def add_edge(u, v):
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # Base triangle: vertices 0 = T, 1 = F, 2 = B.
    add_edge(0, 1)
    add_edge(0, 2)
    add_edge(1, 2)
    n = 3

    # Variable gadgets.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        p = n
        q = n + 1
        n += 2
        pos[v] = p
        neg[v] = q
        add_edge(p, q)
        add_edge(p, 2)
        add_edge(q, 2)

    def literal_vertex(literal):
        v = abs(literal)
        return pos[v] if literal > 0 else neg[v]

    # Clause gadgets.
    for clause in clauses:
        a = n
        b = n + 1
        c = n + 2
        n += 3
        add_edge(a, b)
        add_edge(b, c)
        add_edge(a, c)
        add_edge(a, literal_vertex(clause[0]))
        add_edge(b, literal_vertex(clause[1]))
        add_edge(c, literal_vertex(clause[2]))

    # Canonicalise and remove duplicates (the target format forbids both
    # [u, v] and [v, u], and repeated edges).
    seen = set()
    unique_edges = []
    for u, v in edges:
        key = (u, v)
        if key not in seen:
            seen.add(key)
            unique_edges.append([u, v])

    return {"n": n, "edges": unique_edges}

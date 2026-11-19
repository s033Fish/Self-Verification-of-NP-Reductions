"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

SOURCE: NaeThreeSat  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
TARGET: ThreeColoring {"n": n, "edges": [[u, v], ...]}

Construction
------------
Use a base triangle of three "colour" vertices:

    T = 0, F = 1, B = 2      (edges T-F, F-B, T-B)

For every variable v (1..m) create two vertices pos(v) and neg(v):

    pos(v) -- neg(v)
    pos(v) -- B
    neg(v) -- B

Because both are adjacent to B they can only take colours T/F, and the
edge pos(v)--neg(v) forces them to differ.  So a colouring encodes a
truth assignment (pos(v)=T means v true, pos(v)=F means v false).

For every clause (l1, l2, l3) create three fresh vertices u, v, w forming
a triangle (u-v, v-w, u-w) and add the edges

    lit(l1) -- u,   lit(l2) -- v,   lit(l3) -- w

where lit(+x)=pos(x) and lit(-x)=neg(x).  The three literal vertices are
coloured T/F only.  If all three literal colours were equal, then u, v, w
would all have to avoid that colour, but a triangle needs all three
colours -- impossible.  If the literal colours are not all equal, an
explicit valid colouring of {u, v, w} exists (e.g. for colours T,T,F take
u=F, v=B, w=T).  Gadgets only touch their own fresh vertices and their
three literals, so they combine independently.

Hence the graph is 3-colourable iff the formula has a not-all-equal
satisfying assignment.
"""

BASE_T, BASE_F, BASE_B = 0, 1, 2


def reduce(instance):
    """Return a 3-Coloring instance equivalent to the NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base colour triangle.
    edges = [[BASE_T, BASE_F], [BASE_F, BASE_B], [BASE_T, BASE_B]]

    # Literal vertices for each variable.
    pos = {}
    neg = {}
    next_vertex = 3
    for v in range(1, num_vars + 1):
        p = next_vertex
        n = next_vertex + 1
        next_vertex += 2
        pos[v] = p
        neg[v] = n
        edges.append([p, n])
        edges.append([p, BASE_B])
        edges.append([n, BASE_B])

    def literal_vertex(literal):
        if literal > 0:
            return pos[literal]
        return neg[-literal]

    # Clause gadgets.
    for clause in clauses:
        u = next_vertex
        v = next_vertex + 1
        w = next_vertex + 2
        next_vertex += 3
        edges.append([u, v])
        edges.append([v, w])
        edges.append([u, w])
        edges.append([literal_vertex(clause[0]), u])
        edges.append([literal_vertex(clause[1]), v])
        edges.append([literal_vertex(clause[2]), w])

    return {"n": next_vertex, "edges": edges}

"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Start with a base triangle on three vertices:

    0 = TRUE, 1 = FALSE, 2 = BASE

For every variable v in 1..m create two literal vertices pos[v] and neg[v],
join them to each other and to BASE.  Since BASE has colour 2, each literal
vertex is forced to colour 0 or 1, and pos[v]/neg[v] must differ: they encode
the truth value of v.

For every clause (l1, l2, l3) create a fresh triangle a, b, c and connect a to
the vertex of l1, b to the vertex of l2 and c to the vertex of l3.  A triangle
needs three distinct colours, while each of a, b, c is forbidden one colour
(that of its literal, which is 0 or 1).  Such a triangle is 3-colourable iff
the three literal colours are not all equal, i.e. iff the clause is
not-all-equal satisfied.

The graph is 3-colourable iff the formula has a not-all-equal satisfying
assignment.  The construction uses O(m + k) vertices and edges.
"""

from problems import NaeThreeSat, ThreeColoring


def reduce(instance):
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance."""
    NaeThreeSat.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    def add_edge(u, v):
        # The construction never creates self loops or duplicate edges, but
        # guard anyway so the output is always a valid graph instance.
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append([u, v])

    TRUE, FALSE, BASE = 0, 1, 2
    add_edge(TRUE, FALSE)
    add_edge(FALSE, BASE)
    add_edge(TRUE, BASE)

    pos = {}
    neg = {}
    next_id = 3
    for var in range(1, num_vars + 1):
        p = next_id
        next_id += 1
        n = next_id
        next_id += 1
        pos[var] = p
        neg[var] = n
        add_edge(p, n)
        add_edge(p, BASE)
        add_edge(n, BASE)

    def literal_vertex(literal):
        if literal > 0:
            return pos[literal]
        return neg[-literal]

    for clause in clauses:
        a = next_id
        next_id += 1
        b = next_id
        next_id += 1
        c = next_id
        next_id += 1
        add_edge(a, b)
        add_edge(b, c)
        add_edge(a, c)
        add_edge(a, literal_vertex(clause[0]))
        add_edge(b, literal_vertex(clause[1]))
        add_edge(c, literal_vertex(clause[2]))

    result = {"n": next_id, "edges": edges}
    ThreeColoring.validate(result)
    return result

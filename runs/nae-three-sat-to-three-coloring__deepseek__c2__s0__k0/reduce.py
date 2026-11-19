"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Start with a base triangle on vertices

    T = 0, F = 1, B = 2

so that in any proper 3-colouring these three vertices receive the three
distinct colours.  Think of T's colour as "true", F's colour as "false" and
B's colour as a neutral "base" colour.

Variable gadget
~~~~~~~~~~~~~~~
For each variable v (1..m) create two vertices

    pos(v) and neg(v)

with edges pos(v)-neg(v), pos(v)-B and neg(v)-B.  Since both are adjacent
to B they can only use the colours of T and F, and the edge between them
forces those two colours to be different.  Thus in every proper colouring
exactly one of pos(v), neg(v) has the "true" colour and the other the
"false" colour; this encodes a truth assignment.

Clause gadget
~~~~~~~~~~~~~
For each clause (l1, l2, l3) create three fresh vertices c1, c2, c3 forming
a triangle, and connect ci to the vertex representing li.

Correctness
~~~~~~~~~~~
A clause triangle must use all three colours, in particular the base
colour B.  If all three literals of a clause had the same colour (all
"true" or all "false"), then none of c1, c2, c3 could take that colour and
the triangle could only use the two remaining colours -- impossible.  So
every proper colouring yields a NAE-satisfying assignment.

Conversely, if the literals are not all equal, say their colours are a mix
of "true" and "false", the triangle can always be coloured: give c1, c2, c3
the three colours so that ci avoids the colour of li (a short case check
shows this is always possible for a non-constant pattern).

The formula is NAE-satisfiable iff the constructed graph is 3-colourable.
The construction uses O(m + number of clauses) vertices and edges, hence
runs in polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: T, F, B.
    T, F, B = 0, 1, 2
    edges = {(T, F), (F, B), (T, B)}

    def add_edge(u, w):
        if u == w:
            return
        edges.add((u, w) if u < w else (w, u))

    # Variable gadgets.
    pos = {}
    neg = {}
    next_vertex = 3
    for v in range(1, num_vars + 1):
        pos[v] = next_vertex
        neg[v] = next_vertex + 1
        next_vertex += 2
        add_edge(pos[v], neg[v])
        add_edge(pos[v], B)
        add_edge(neg[v], B)

    def literal_vertex(lit):
        v = abs(lit)
        return pos[v] if lit > 0 else neg[v]

    # Clause gadgets.
    for clause in clauses:
        c1 = next_vertex
        c2 = next_vertex + 1
        c3 = next_vertex + 2
        next_vertex += 3
        add_edge(c1, c2)
        add_edge(c2, c3)
        add_edge(c1, c3)
        for c, lit in zip((c1, c2, c3), clause):
            add_edge(c, literal_vertex(lit))

    return {"n": next_vertex, "edges": [list(e) for e in sorted(edges)]}

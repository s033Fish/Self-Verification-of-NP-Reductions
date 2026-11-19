"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Fix three base vertices with all three pairwise edges (a triangle), which
force the three colours to be distinct.  Call them T = 0, F = 1, B = 2.

Variable gadget
    For every variable v in 1..num_vars create vertices pos[v] and neg[v],
    add the edge (pos[v], neg[v]) and connect both to the base vertex B.
    Together with B these form a triangle, so pos[v] and neg[v] receive the
    two colours T and F in some order.  A literal +v is represented by
    pos[v] and a literal -v by neg[v]; thus every literal vertex is coloured
    T (true) or F (false), never B.

Clause gadget
    For a clause (l1, l2, l3) create a fresh triangle (u, v, w) and add the
    edges (lit(l1), u), (lit(l2), v), (lit(l3), w).  The triangle forces u, v,
    w to take all three distinct colours, with u != colour(l1), etc.
    If l1, l2, l3 all had the same colour (all true or all false), then u, v, w
    would each have to avoid that colour and still be pairwise distinct, which
    is impossible with only two remaining colours.  Conversely, whenever the
    three literals are not all equal, a valid colouring of u, v, w exists (it
    can be chosen independently for every clause).  Hence the clause gadget is
    colour-able exactly when the clause is not all-equal.

The graph is therefore 3-colourable iff the NAE-3-SAT instance is satisfiable.
It has 3 + 2*num_vars + 3*num_clauses vertices and O(num_vars + num_clauses)
edges, so the construction is polynomial time.
"""


def reduce(instance):
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance.

    instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    returns:  {"n": n, "edges": [[u, v], ...]}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    T, F, B = 0, 1, 2
    edges = [[T, F], [F, B], [T, B]]

    pos = {}
    neg = {}
    n = 3
    for var in range(1, num_vars + 1):
        pos[var] = n
        neg[var] = n + 1
        n += 2
        edges.append([pos[var], neg[var]])
        edges.append([pos[var], B])
        edges.append([neg[var], B])

    def literal_vertex(literal):
        if literal > 0:
            return pos[literal]
        return neg[-literal]

    for clause in clauses:
        u = n
        v = n + 1
        w = n + 2
        n += 3
        edges.append([u, v])
        edges.append([v, w])
        edges.append([u, w])
        edges.append([literal_vertex(clause[0]), u])
        edges.append([literal_vertex(clause[1]), v])
        edges.append([literal_vertex(clause[2]), w])

    return {"n": n, "edges": edges}

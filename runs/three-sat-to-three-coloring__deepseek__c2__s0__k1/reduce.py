"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Construction
------------
Palette: three mutually adjacent vertices T (true), F (false), B (base).
Every literal vertex is adjacent to B, so it is coloured either T or F.

Variable gadget (variable v):
    vertices p_v, n_v with edges (p_v, n_v), (p_v, B), (n_v, B).
    This forces p_v and n_v to receive opposite colours among {T, F}.

OR gadget  G(x, y) -> o  with internal vertices p, q:
    triangle (o, p, q), edges (p, x), (q, y) and (o, B).
    With o restricted to {T, F} by the edge to B:
        * if x = y = F then o is forced to F;
        * if x = T or y = T then o can be coloured T.
    Hence the gadget is colour-consistent with o = T exactly when
    x OR y is true.

Clause gadget for (l1 v l2 v l3):
    o1 = OR(l1, l2),  o2 = OR(o1, l3),  plus edge (o2, F).
    The edge (o2, F) together with (o2, B) forces o2 = T.
    If all literals are false, o1 = F and then o2 = F, contradicting the
    forced T.  If some literal is true, o1 and/or o2 can be coloured T and
    the gadget is satisfiable.  Thus the clause is satisfiable iff its
    gadget is 3-colourable.

The whole graph is 3-colourable iff the formula is satisfiable.  The
construction is linear in the size of the formula.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a 3-Coloring instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    next_id = 0

    def new_vertex():
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    def add_edge(u, v):
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # Palette triangle: T (true), F (false), B (base).
    T = new_vertex()
    F = new_vertex()
    B = new_vertex()
    add_edge(T, F)
    add_edge(F, B)
    add_edge(T, B)

    # Variable gadgets.
    pos = [0] * (m + 1)
    neg = [0] * (m + 1)
    for v in range(1, m + 1):
        p = new_vertex()
        n = new_vertex()
        pos[v] = p
        neg[v] = n
        add_edge(p, n)
        add_edge(p, B)
        add_edge(n, B)

    def literal_vertex(lit):
        if lit > 0:
            return pos[lit]
        return neg[-lit]

    # Clause gadgets.
    for clause in clauses:
        l1, l2, l3 = clause[0], clause[1], clause[2]
        x1 = literal_vertex(l1)
        x2 = literal_vertex(l2)
        x3 = literal_vertex(l3)

        # First OR: o1 = x1 OR x2.
        o1 = new_vertex()
        p1 = new_vertex()
        q1 = new_vertex()
        add_edge(o1, p1)
        add_edge(p1, q1)
        add_edge(o1, q1)
        add_edge(p1, x1)
        add_edge(q1, x2)
        add_edge(o1, B)

        # Second OR: o2 = o1 OR x3.
        o2 = new_vertex()
        p2 = new_vertex()
        q2 = new_vertex()
        add_edge(o2, p2)
        add_edge(p2, q2)
        add_edge(o2, q2)
        add_edge(p2, o1)
        add_edge(q2, x3)
        add_edge(o2, B)

        # Force o2 to be true (colour of T) by making it adjacent to F and B.
        add_edge(o2, F)

    # Deduplicate (edges are already unique, but keep it robust).
    seen = set()
    unique_edges = []
    for u, v in edges:
        if (u, v) not in seen:
            seen.add((u, v))
            unique_edges.append([u, v])

    return {"n": next_id, "edges": unique_edges}

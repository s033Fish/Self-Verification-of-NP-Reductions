"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

SOURCE: NaeThreeSat  instance {"num_vars": m, "clauses": [[l1,l2,l3],...]}
TARGET: ThreeColoring instance {"n": n, "edges": [[u,v],...]}

Construction
------------
Palette: a triangle on vertices B (base), T, F.  Every variable vertex is
adjacent to B, so it cannot take B's colour; the two remaining colours act as
the truth values.

For each variable v in 1..m create vertices pos(v) and neg(v) joined by an
edge and both joined to B.  Thus pos(v) and neg(v) receive the two colours
different from colour(B), and they differ from each other, so they encode a
consistent truth assignment (literal +v is "true" when pos(v) has one fixed
colour, -v when it has the other).

For each clause (l1,l2,l3) create a fresh triangle (u,v,w) and join the
literal vertices a,b,c of l1,l2,l3 to u,v,w respectively.  Claim: this gadget
is 3-colourable (with a,b,c already coloured from the two non-B colours)
exactly when a,b,c are not all equal.
  * If a=b=c then u,v,w must all avoid that colour, leaving only two colours
    for a triangle, impossible.
  * If a,b,c are not all equal one can always extend (verified by the tests).
Hence the whole graph is 3-colourable iff the formula has a not-all-equal
satisfying assignment.

The graph has n = 3 + 2*m + 3*(#clauses) vertices and O(m + #clauses) edges,
so the reduction is polynomial (indeed linear) time.
"""

from __future__ import annotations


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    def add(u, v):
        edges.append([u, v])

    # Palette triangle: B = 0, T = 1, F = 2.
    B, T, F = 0, 1, 2
    add(B, T)
    add(T, F)
    add(F, B)

    # Variable vertices.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        p = 3 + 2 * (v - 1)
        n = p + 1
        pos[v] = p
        neg[v] = n
        add(p, n)   # literal and its negation differ
        add(p, B)   # both differ from the base colour
        add(n, B)

    def literal_vertex(lit):
        v = abs(lit)
        return pos[v] if lit > 0 else neg[v]

    # Clause gadgets.
    next_vertex = 3 + 2 * num_vars
    for clause in clauses:
        u = next_vertex
        v = next_vertex + 1
        w = next_vertex + 2
        next_vertex += 3
        # fresh triangle
        add(u, v)
        add(v, w)
        add(w, u)
        # connect the three literals
        a = literal_vertex(clause[0])
        b = literal_vertex(clause[1])
        c = literal_vertex(clause[2])
        add(a, u)
        add(b, v)
        add(c, w)

    return {"n": next_vertex, "edges": edges}

"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction (standard):
  * Base triangle with vertices 0 (ground G), 1 (T), 2 (F).
  * For each variable v in 1..m, two literal vertices:
        pos(v) = 3 + 2*(v-1)   (represents +v)
        neg(v) = 3 + 2*(v-1)+1 (represents -v)
    Edges: pos(v)-neg(v), pos(v)-0, neg(v)-0.  This forces pos/neg to take
    the two non-ground colours (T and F), one each.
  * For each clause (l1,l2,l3), add a triangle a,b,c and connect a to the
    vertex of l1, b to l2, c to l3.  A triangle must use all three colours;
    it is properly attached iff the three literal colours are not all equal.
"""

from __future__ import annotations


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = [[0, 1], [1, 2], [0, 2]]  # base triangle: 0=ground, 1=T, 2=F

    def lit_vertex(lit):
        base = 3 + 2 * (abs(lit) - 1)
        return base if lit > 0 else base + 1

    # Variable gadgets.
    for v in range(1, m + 1):
        p = 3 + 2 * (v - 1)
        q = p + 1
        edges.append([p, q])
        edges.append([p, 0])
        edges.append([q, 0])

    n = 3 + 2 * m

    # Clause gadgets.
    for clause in clauses:
        a, b, c = n, n + 1, n + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        edges.append([a, lit_vertex(clause[0])])
        edges.append([b, lit_vertex(clause[1])])
        edges.append([c, lit_vertex(clause[2])])
        n += 3

    return {"n": n, "edges": edges}

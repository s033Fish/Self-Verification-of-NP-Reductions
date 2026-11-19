"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Construction
------------
Let the formula have m variables (1..m) and t clauses.

Vertices:
  * For each variable v in 1..m, a triangle gadget with vertices
        x_v      = 2*(v-1)        (literal +v)
        nx_v     = 2*(v-1) + 1    (literal -v)
        d_v      = 2*m + (v-1)    (dummy)
    and triangle edges (x_v, nx_v), (x_v, d_v), (nx_v, d_v).
  * For each clause j (0-based), a clause vertex
        c_j      = 3*m + j
    joined to the literal vertices of its three literals.

Set k = m (the number of variables).

Why it is correct
-----------------
(<=) If the formula is satisfiable, pick for every variable v the literal
vertex that is made true.  These m vertices dominate both literal vertices
of the gadget and the dummy d_v.  Every clause vertex is adjacent to at
least one true literal, hence dominated.  So a dominating set of size m
exists.

(=>) The closed neighbourhood of d_v is exactly {d_v, x_v, nx_v}, and these
gadgets are pairwise disjoint, so any dominating set must contain at least
one vertex of each gadget: |D| >= m.  If |D| <= m then |D| = m and D
contains exactly one vertex per gadget, hence no clause vertex.  Every
clause vertex must then be dominated by one of its literals that lies in D.
Interpreting a chosen literal vertex as making that literal true (and
choosing an arbitrary value when d_v is chosen) turns every clause true, so
the formula is satisfiable.

The graph has 3m + t vertices and O(m + t) edges, so the reduction is
polynomial time.
"""

from __future__ import annotations


def _literal_vertex(literal: int) -> int:
    v = abs(literal)
    base = 2 * (v - 1)
    return base if literal > 0 else base + 1


def reduce(instance):
    """Map a 3-SAT instance to a Dominating Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    t = len(clauses)

    edges = []
    # Variable gadgets: triangle (x_v, nx_v, d_v).
    for v in range(1, m + 1):
        x = _literal_vertex(v)
        nx = _literal_vertex(-v)
        d = 2 * m + (v - 1)
        edges.append([x, nx])
        edges.append([x, d])
        edges.append([nx, d])

    # Clause vertices joined to their literals.
    for j, clause in enumerate(clauses):
        c = 3 * m + j
        for literal in clause:
            edges.append([c, _literal_vertex(literal)])

    n = 3 * m + t
    return {"n": n, "edges": edges, "k": m}

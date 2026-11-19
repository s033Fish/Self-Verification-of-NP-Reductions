"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Given a 3-SAT instance with m variables and c clauses, build a graph G with:

  * two vertices per variable v: 2*(v-1) representing the literal +v and
    2*(v-1)+1 representing the literal -v, joined by an edge (the variable
    gadget);
  * one vertex per clause, numbered 2*m + j for clause j.  Clause vertices
    have NO edges to anything (they are isolated);
  * for every clause j and every literal l in it, an edge between the clause
    vertex and the literal vertex of l.

Set k = m + c.

Why this works
--------------
(=>) If the formula has a satisfying assignment, take the literal vertex of
each variable that is set true, plus every clause vertex.  This is m + c
vertices.  Every variable gadget is dominated (the chosen literal vertex
dominates itself and its partner).  Every clause vertex is in the set.  Every
literal vertex is dominated by its own variable's chosen vertex.  So it is a
dominating set of size k.

(<=) Suppose D dominates G with |D| <= k = m + c.  The c clause vertices are
isolated, so each of them must itself be in D; that already uses c vertices.
Every variable gadget is an isolated edge (its two vertices are adjacent only
to each other and to clause vertices), so D must contain at least one of its
two vertices; otherwise both endpoints of that edge are undominated (a clause
vertex in D is not adjacent to them because clause vertices are isolated).
Hence |D| >= c + m = k, so |D| = k, D contains exactly one vertex of every
variable gadget and all clause vertices, and no other vertices.  Assign each
variable the truth value of the chosen literal.  Every clause vertex is
adjacent to the literal vertex chosen for one of its literals, and that
literal vertex is in D, so the clause contains a true literal.  The
assignment satisfies the formula.

Edge cases
----------
* c = 0: G has m disjoint edges, k = m; the empty assignment satisfies the
  formula and one endpoint per edge dominates.  (m = 0 gives the empty graph
  and k = 0, also yes.)
* k is always >= 0, and k >= n never happens here (k = m + c and
  n = 2m + c > k for m > 0; for m = 0, n = c = k, which is fine).

The construction runs in time O(m + total literals), i.e. polynomial.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 2 * num_vars + len(clauses)
    edges = []

    # Variable gadgets: literal vertex of +v is 2*(v-1), of -v is 2*(v-1)+1.
    for v in range(1, num_vars + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    def literal_vertex(literal: int) -> int:
        v = abs(literal)
        base = 2 * (v - 1)
        return base if literal > 0 else base + 1

    # Clause vertices (isolated) joined to their three literal vertices.
    for j, clause in enumerate(clauses):
        clause_vertex = 2 * num_vars + j
        for literal in clause:
            edges.append([clause_vertex, literal_vertex(literal)])

    k = num_vars + len(clauses)
    return {"n": n, "edges": edges, "k": k}

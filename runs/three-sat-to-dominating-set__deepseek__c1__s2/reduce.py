"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Source instance:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance:  {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Vertices are laid out as follows.

* For every variable v in 1..m there is a triangle on the three vertices

      T_v = 3*(v-1)      (literal +v is true)
      F_v = 3*(v-1) + 1  (literal -v is true)
      Z_v = 3*(v-1) + 2  (auxiliary)

  with edges (T_v, F_v), (T_v, Z_v), (F_v, Z_v).  Z_v is adjacent only to
  T_v and F_v, so any dominating set must contain T_v or F_v.  These m
  requirements are on disjoint vertex sets, hence every dominating set has
  at least m vertices.

* For every clause j (0-based) there is one vertex

      C_j = 3*m + j

  with one edge to the literal-vertex of each of the clause's three
  literals: +v maps to T_v, -v maps to F_v.

The target budget is k = m.

Correctness
-----------
(<=) If the formula is satisfiable, take the literal-vertex of a true
literal for each variable (m vertices).  In each variable triangle the
chosen vertex dominates the other two, and every clause vertex is adjacent
to a chosen literal-vertex because its clause contains a true literal.
So the graph has a dominating set of size m.

(=>) Suppose D is a dominating set with |D| <= m.  For each variable v,
Z_v must be dominated, and its only neighbours are T_v and F_v, so D
contains T_v or F_v.  This gives at least m distinct vertices, so |D| = m,
D contains exactly one literal-vertex per variable and contains no clause
vertex.  Every clause vertex C_j must therefore be dominated by one of its
literal-vertices in D, i.e. the assignment induced by D (set v true iff
T_v in D) satisfies every clause.  Hence the formula is satisfiable.

All graphs produced are simple (no loops, no repeated edges) and the
construction runs in O(m + total literals) time.
"""

from __future__ import annotations


def reduce(instance):
    """Return a Dominating Set instance equivalent to the 3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    def true_vertex(v):
        return 3 * (v - 1)

    def false_vertex(v):
        return 3 * (v - 1) + 1

    def aux_vertex(v):
        return 3 * (v - 1) + 2

    edges = []

    # Variable gadgets: one triangle per variable.
    for v in range(1, m + 1):
        t = true_vertex(v)
        f = false_vertex(v)
        z = aux_vertex(v)
        edges.append([t, f])
        edges.append([t, z])
        edges.append([f, z])

    # Clause gadgets: one vertex per clause, joined to its literal vertices.
    for j, clause in enumerate(clauses):
        c = 3 * m + j
        for literal in clause:
            if literal > 0:
                edges.append([c, true_vertex(literal)])
            else:
                edges.append([c, false_vertex(-literal)])

    return {
        "n": 3 * m + len(clauses),
        "edges": edges,
        "k": m,
    }

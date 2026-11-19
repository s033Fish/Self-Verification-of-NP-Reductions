"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Let the 3-SAT instance have m variables and q clauses.

Vertex numbering (n = 3m + 3q):

  Variable gadget for variable v (1..m), base = 3*(v-1):
      x  = base      (literal +v)
      nx = base + 1  (literal -v)
      p  = base + 2
      edges: x-nx, x-p, nx-p   (a triangle)

  Clause gadget for clause j (0..q-1), base = 3m + 3*j:
      a = base, b = base+1, c = base+2
      edge a-c
      for each literal l of the clause:
          edge a - literal_vertex(l)
          edge b - literal_vertex(l)

Budget: k = m + q.

Correctness
-----------
(<=) Given a satisfying assignment, take D = {one true literal vertex per
variable} union {c_j for every clause j}.  |D| = m + q.  Each variable
triangle is dominated by its chosen literal vertex; in each clause gadget
c_j dominates a_j and c_j, and b_j is adjacent to the clause's true literal.
So D dominates.

(=>) Let D dominate with |D| <= m+q.
  * p_v is adjacent only to x_v, nx_v, p_v, so D must contain at least one
    vertex of every variable gadget: at least m vertices, and if both x_v and
    nx_v were in D for some v that gadget would use >= 2.
  * c_j is adjacent only to a_j, c_j, so D contains a_j or c_j.
  * b_j is adjacent only to b_j and the clause's three literal vertices, so
    if no literal of clause j lies in D then b_j in D; together with the
    previous point the gadget then uses >= 2 vertices.
  Hence |D| >= m + 2q - t, where t is the number of clauses having a literal
  in D.  Since |D| <= m+q, t = q and no variable gadget contains both x_v
  and nx_v.  Setting variable v true iff x_v in D (arbitrary if neither)
  makes, for every clause, one of its literals true.  So the formula is
  satisfiable.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Dominating Set instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    q = len(clauses)

    edges: list[list[int]] = []

    # literal vertex of variable v for a signed literal
    def lit_vertex(literal: int) -> int:
        base = 3 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    # variable gadgets
    for v in range(1, m + 1):
        x = 3 * (v - 1)
        nx = x + 1
        p = x + 2
        edges.append([x, nx])
        edges.append([x, p])
        edges.append([nx, p])

    # clause gadgets
    for j, clause in enumerate(clauses):
        base = 3 * m + 3 * j
        a = base
        b = base + 1
        c = base + 2
        edges.append([a, c])
        for literal in clause:
            lv = lit_vertex(literal)
            edges.append([a, lv])
            edges.append([b, lv])

    n = 3 * m + 3 * q
    k = m + q
    return {"n": n, "edges": edges, "k": k}

"""Polynomial-time reduction from 3-SAT to Dominating Set.

Instance format (source, 3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Variables are 1..m, a literal is +v or -v.

Instance format (target, Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
* Each variable v in 1..m becomes a triangle of three vertices:
      x_v   (literal  +v)
      nx_v  (literal  -v)
      p_v
  with edges (x_v, nx_v), (x_v, p_v), (nx_v, p_v).  The two literal
  vertices x_v and nx_v are the only vertices shared with clause gadgets.
* Each clause c becomes two new vertices a_c, b_c.  Both are adjacent to
  the three literal vertices of c and to nothing else; a_c and b_c are not
  adjacent to each other.
* The budget is k = m.

Why it is correct
-----------------
Satisfiable => dominating set of size m:
    Take, for every variable, the literal vertex that is true under a
    satisfying assignment.  These m vertices dominate each variable
    triangle (a literal vertex is adjacent to the other two triangle
    vertices).  Every clause contains a true literal, whose vertex is
    adjacent to both a_c and b_c, so every clause gadget is dominated.

Dominating set of size <= m => satisfiable:
    For each variable v, the closed neighbourhood of p_v is exactly
    {x_v, nx_v, p_v}, and these m sets are pairwise disjoint.  Hence any
    dominating set contains at least m vertices, one from each such set.
    If |D| <= m then |D| = m and D contains no clause-gadget vertex: D
    holds exactly one vertex of each variable triangle.  Since a_c and b_c
    are non-adjacent and their only neighbours are the literal vertices of
    c, some literal vertex of c must lie in D.  Setting the literal of each
    variable that appears in D to true (and the remaining variables to
    false) satisfies every clause.

The construction uses 3m + 2*|clauses| vertices and 3m + 6*|clauses| edges,
so it runs in polynomial time.  Edge cases: m = 0 with no clauses yields the
empty graph with k = 0 (yes), and a formula with no clauses yields m disjoint
triangles with k = m (yes, one vertex per triangle).
"""

from __future__ import annotations


def _literal_vertex(literal: int) -> int:
    """Vertex index of a literal: 3*(v-1) for +v, 3*(v-1)+1 for -v."""
    variable = abs(literal)
    return 3 * (variable - 1) + (0 if literal > 0 else 1)


def reduce(instance):
    """Reduce a 3-SAT instance to a Dominating Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    # Variable gadgets: one triangle per variable.
    for variable in range(1, num_vars + 1):
        base = 3 * (variable - 1)
        x, nx, p = base, base + 1, base + 2
        edges.append([x, nx])
        edges.append([x, p])
        edges.append([nx, p])

    n = 3 * num_vars
    # Clause gadgets: two vertices adjacent to all three literal vertices.
    for clause in clauses:
        a, b = n, n + 1
        n += 2
        for literal in clause:
            lit_vertex = _literal_vertex(literal)
            edges.append([a, lit_vertex])
            edges.append([b, lit_vertex])

    return {"n": n, "edges": edges, "k": num_vars}

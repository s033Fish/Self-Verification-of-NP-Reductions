"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Gadget construction
-------------------
We use three colours {0, 1, 2}.  Colour 0 is a reserved "base" colour.

* One base vertex B (vertex 0), coloured 0.
* For each variable v in 1..m two vertices:
      x_v  = 2v - 1      (representing the literal  +v)
      nx_v = 2v          (representing the literal  -v)
  with edges (B, x_v), (B, nx_v) and (x_v, nx_v).  Hence x_v and nx_v must
  receive the two colours different from 0, i.e. {1, 2}, and they differ.
  We read colour 1 as "true" and colour 2 as "false" (the opposite reading
  works equally well).

* For each clause (l1, l2, l3) three fresh vertices c1, c2, c3 forming a
  triangle, with ci joined to the variable vertex of literal li.

Correctness
-----------
A clause triangle needs its three vertices to have three distinct colours.
If all three literals of a clause evaluate true, all three literal vertices
have colour 1, so each ci must avoid colour 1 and can only use {0, 2}: not
three distinct colours.  Symmetrically all-false (colour 2) is impossible.
If the literals are mixed, one can always pick a permutation of {0,1,2}
for (c1, c2, c3) with ci != colour(li): for literal-colour patterns
(1,1,2) -> (0,2,1), (1,2,1) -> (2,1,0), (1,2,2) -> (2,0,1), etc.
So a clause gadget is 3-colourable exactly when its literals are not all
equal.  The gadgets only interact through the variable vertices, so the
whole graph is 3-colourable iff the formula has a not-all-equal satisfying
assignment.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance.

    instance = {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    returns    {"n": n, "edges": [[u, v], ...]}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Base vertex 0, reserved colour 0.
    base = 0

    def var_vertex(literal):
        v = abs(literal)
        return 2 * v - 1 if literal > 0 else 2 * v

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        x_true = 2 * v - 1
        x_false = 2 * v
        edges.append([base, x_true])
        edges.append([base, x_false])
        edges.append([x_true, x_false])

    # Clause gadgets.
    next_vertex = 2 * num_vars + 1
    for clause in clauses:
        c1, c2, c3 = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        edges.append([c1, c2])
        edges.append([c2, c3])
        edges.append([c1, c3])
        for c, literal in zip((c1, c2, c3), clause):
            edges.append([c, var_vertex(literal)])

    n = next_vertex  # vertices are 0 .. next_vertex-1
    return {"n": n, "edges": edges}

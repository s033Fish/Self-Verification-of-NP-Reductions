"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

SOURCE: ThreeColoring  instance {"n": n, "edges": [[u, v], ...]}
TARGET: OneInThreeSat  instance {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour c in {0,1,2} we introduce a boolean variable
    x[v, c]   (true  <=>  vertex v receives colour c).

* For each vertex v we add the clause
      (x[v,0], x[v,1], x[v,2])
  which is a 1-in-3 clause: exactly one colour is chosen for v.

* For each edge (u, v) and each colour c we add a fresh variable z and the
  clause
      (x[u,c], x[v,c], z).
  This clause is satisfiable exactly when NOT both x[u,c] and x[v,c] are true:
  if both were true the clause would contain two true variables (violating
  "exactly one"), while otherwise z can be set to make exactly one true.
  Hence it forbids u and v from sharing colour c.

The formula is satisfiable iff the graph has a proper 3-colouring, and the
construction uses 3n + 3|E| variables and n + 3|E| clauses, so it is
polynomial-time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-Coloring instance to a 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        # variables are 1..num_vars; v in 0..n-1, c in 0..2
        return 3 * v + c + 1

    clauses = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Forbid the two endpoints of an edge from sharing a colour.
    next_var = 3 * n + 1
    for u, w in edges:
        for c in range(3):
            z = next_var
            next_var += 1
            clauses.append([var(u, c), var(w, c), z])

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Encoding
--------
For every vertex v and colour c in {0,1,2} we create a boolean variable
x(v,c) = 3*v + c + 1, meaning "vertex v gets colour c".

* Exactly-one-colour constraint: for each vertex v the clause
      [x(v,0), x(v,1), x(v,2)]
  is a 1-in-3 clause, so exactly one colour is true for v.

* Edge constraint: for each edge {u,v} and each colour c we create a fresh
  variable y(u,v,c) and the clause
      [x(u,c), x(v,c), y(u,v,c)].
  A 1-in-3 clause forbids x(u,c) and x(v,c) being true together, i.e. it
  forbids u and v sharing colour c.  If u and v do have different colours,
  then for the two colours used by them exactly one of x(u,c),x(v,c) is true
  (forcing y false) and for the third colour both are false (forcing y
  true); this is consistent, so no spurious constraint is added.

Hence the formula is 1-in-3 satisfiable iff the graph is 3-colourable.
The construction uses 3*n + 3*|E| variables and n + 3*|E| clauses, so it
runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    clauses = []

    # Vertex variables occupy 1 .. 3*n.
    for v in range(n):
        base = 3 * v + 1
        clauses.append([base, base + 1, base + 2])

    # Fresh variables for edge gadgets start after the vertex variables.
    next_var = 3 * n + 1
    for edge in edges:
        u, v = edge[0], edge[1]
        for c in range(3):
            y = next_var
            next_var += 1
            clauses.append([3 * u + c + 1, 3 * v + c + 1, y])

    return {"num_vars": next_var - 1, "clauses": clauses}

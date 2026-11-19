"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance:  {"n": n, "edges": [[u, v], ...]}
Target instance:  {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v in 0..n-1 and colour c in {0, 1, 2} create a boolean
variable x(v, c) = 3*v + c + 1.

* For each vertex v add the clause (x(v,0), x(v,1), x(v,2)).  A 1-in-3
  clause is true exactly when one of its variables is true, so this forces
  every vertex to receive exactly one colour.

* For each edge {u, v} and each colour c add a fresh auxiliary variable
  y(u,v,c) and the clause (x(u,c), x(v,c), y(u,v,c)).  If both endpoints
  had colour c then the clause would contain two true variables and fail.
  Conversely, if at most one of x(u,c), x(v,c) is true, the fresh y can be
  set to make the clause have exactly one true variable.  Hence the clause
  forbids exactly the situation where u and v share colour c.

A proper 3-colouring therefore gives a satisfying assignment (set each y
appropriately), and any satisfying assignment gives a proper 3-colouring
by reading off, for each vertex, the unique true x(v,c).  The construction
uses 3*n + 3*|E| variables and n + 3*|E| clauses, so it is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses = []

    # Exactly one colour per vertex.
    for v in range(n):
        base = 3 * v + 1
        clauses.append([base, base + 1, base + 2])

    # Forbid equal colours on the endpoints of every edge.
    next_var = 3 * n + 1
    for u, v in edges:
        for c in range(3):
            clauses.append([3 * u + c + 1, 3 * v + c + 1, next_var])
            next_var += 1

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour c in {0,1,2} create a variable

    x[v][c] = 3*v + c + 1

meaning "vertex v receives colour c".

1. For every vertex v add the clause

       (x[v][0], x[v][1], x[v][2])

   A positive 1-in-3 clause is true iff exactly one of its variables is
   true, so this forces each vertex to receive exactly one colour.

2. For every edge {u,v} and every colour c add a fresh auxiliary variable
   z and the clause

       (x[u][c], x[v][c], z)

   If both endpoints had colour c then two of the three variables would be
   true and the clause would be false.  Otherwise z can always be chosen to
   make exactly one variable true (z = 1 when neither endpoint has colour c,
   z = 0 when exactly one does).  Hence the clause is equivalent to the
   constraint "not both u and v have colour c".

Therefore a satisfying assignment of the target corresponds exactly to a
proper 3-colouring of the source graph, and vice versa.  The construction
uses 3*n + 3*|E| variables and n + 3*|E| clauses, so it runs in polynomial
time and never calls a solver.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    clauses = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([3 * v + 1, 3 * v + 2, 3 * v + 3])

    # Forbid equal colours on the two endpoints of every edge, colour by
    # colour, using a fresh auxiliary variable for each such constraint.
    next_var = 3 * n + 1
    for u, v in edges:
        for c in range(3):
            clauses.append([3 * u + c + 1, 3 * v + c + 1, next_var])
            next_var += 1

    return {"num_vars": next_var - 1, "clauses": clauses}

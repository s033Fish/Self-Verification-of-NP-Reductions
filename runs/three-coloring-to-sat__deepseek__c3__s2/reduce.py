"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding: for each vertex v in 0..n-1 and each colour c in {0,1,2} we make a
boolean variable x(v,c) meaning "vertex v has colour c".  Variables are numbered
1..3n with x(v,c) = 3*v + c + 1.

Clauses:
  * for every vertex v:            [x(v,0), x(v,1), x(v,2)]      (at least one colour)
  * for every vertex v, c1 < c2:   [-x(v,c1), -x(v,c2)]          (at most one colour)
  * for every edge (u,w), colour c:[-x(u,c), -x(w,c)]            (endpoints differ)

The formula is satisfiable iff the graph is 3-colourable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        return 3 * v + c + 1

    clauses = []
    for v in range(n):
        # at least one colour
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # at most one colour
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    for u, w in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(w, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding: one boolean variable x_{v,c} for every vertex v and colour c in
{0,1,2}, meaning "vertex v gets colour c".

Clauses:
  * For every vertex v: (x_{v,0} or x_{v,1} or x_{v,2})
    -- every vertex gets at least one colour.
  * For every edge {u,v} and every colour c:
        (not x_{u,c} or not x_{v,c})
    -- adjacent vertices never share a colour.

A satisfying assignment of the formula gives a proper 3-colouring (choose,
for each vertex, any true colour variable; the vertex clause guarantees one
exists and the edge clauses guarantee adjacent choices differ).  Conversely
a proper 3-colouring extends to a satisfying assignment by setting exactly
the chosen colour variable of each vertex to true.  Hence the formula is
satisfiable iff the graph is 3-colourable.

Size: num_vars = 3n, clauses = n + 3|E|, so the reduction is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        # variables are 1..3n
        return 3 * v + c + 1

    clauses = []

    # Each vertex must receive at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

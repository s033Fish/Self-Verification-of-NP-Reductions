"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x(v, c), meaning "vertex v receives colour c":

    x(v, c) = 3*v + c + 1        (variables are 1..3n)

Clauses:
  * For each vertex v:  (x(v,0) v x(v,1) v x(v,2))
        at least one colour is chosen.
  * For each vertex v and each pair c < d:
        (not x(v,c) v not x(v,d))
        at most one colour is chosen.
  * For each edge {u,v} and each colour c:
        (not x(u,c) v not x(v,c))
        the endpoints of an edge get different colours.

Every clause must contain exactly 3 literals on 3 distinct variables, so
the 2-literal clauses above are padded with one extra fresh variable y
(shared by all of them).  Replacing a 2-literal clause A by the pair
(A v y), (A v not y) is satisfiability-preserving: if A is false the two
clauses force y both true and false, and if A is true both are satisfied
whatever y is.  Hence the padded formula is satisfiable iff the original
one is.

The result is satisfiable exactly when the graph is 3-colourable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # No vertices: the empty graph is 3-colourable and the empty CNF is
    # satisfiable with 0 variables.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    def var(v, c):
        return 3 * v + c + 1

    # Fresh variable used only to pad 2-literal clauses to 3 literals.
    y = 3 * n + 1

    clauses = []

    for v in range(n):
        # At least one colour.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # At most one colour (padded to 3 literals).
        for c in range(3):
            for d in range(c + 1, 3):
                a = -var(v, c)
                b = -var(v, d)
                clauses.append([a, b, y])
                clauses.append([a, b, -y])

    # Adjacent vertices must have different colours (padded to 3 literals).
    for u, v in edges:
        for c in range(3):
            a = -var(u, c)
            b = -var(v, c)
            clauses.append([a, b, y])
            clauses.append([a, b, -y])

    return {"num_vars": y, "clauses": clauses}

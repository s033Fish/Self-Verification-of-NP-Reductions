"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Target instance (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} we introduce a
boolean variable

    x(v, c) = 3 * v + c + 1          (variables are 1-indexed)

meaning "vertex v receives colour c".

Clauses:
  * At least one colour per vertex:      [x(v,0), x(v,1), x(v,2)]
  * At most one colour per vertex:       [-x(v,c), -x(v,d)]  for c < d
  * Adjacent vertices differ:            [-x(u,c), -x(v,c)]  for every edge
                                         (u,v) and every colour c

A satisfying assignment chooses exactly one colour per vertex (the first two
families) and gives adjacent vertices different colours (the third family),
i.e. it is exactly a proper 3-colouring.  Conversely every proper 3-colouring
extends to a satisfying assignment by setting x(v,c) true iff v has colour c.

The encoding uses 3n variables and O(n^2 + |E|) clauses, so it runs in
polynomial time.  For n = 0 the result is the empty CNF, which is satisfiable.
"""


def reduce(instance):
    """Return a SAT instance equivalent to the given 3-Coloring instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n

    def var(vertex, colour):
        # Variable for "vertex gets colour", numbered from 1.
        return 3 * vertex + colour + 1

    clauses = []

    for v in range(n):
        # At least one colour.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # At most one colour.
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    for u, v in edges:
        for c in range(3):
            # The two endpoints of an edge must not share a colour.
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance:  {"n": n, "edges": [[u, v], ...]}
Target instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} introduce a
Boolean variable

    x(v, c) = 3*v + c + 1        (so variables are 1..3n)

with the intended meaning "vertex v receives colour c".

Clauses:
  * For each vertex v:  [x(v,0), x(v,1), x(v,2)]
        at least one colour is chosen.
  * For each vertex v and each pair of distinct colours a < b:
        [-x(v,a), -x(v,b)]
        at most one colour is chosen.
  * For each edge {u,v} and each colour c:
        [-x(u,c), -x(v,c)]
        the endpoints do not share colour c.

A satisfying assignment of the formula picks exactly one colour per vertex
and gives adjacent vertices different colours, i.e. a proper 3-colouring.
Conversely a proper 3-colouring extends to a satisfying assignment by
setting x(v,c) true exactly for the colour of v.

The formula has 3n variables and n + 3n + 3|E| = O(n + |E|) clauses, each
of constant size, so the reduction runs in polynomial time and is computed
without any search.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    for v in range(n):
        base = 3 * v
        # At least one colour for vertex v.
        clauses.append([base + 1, base + 2, base + 3])
        # At most one colour for vertex v.
        clauses.append([-(base + 1), -(base + 2)])
        clauses.append([-(base + 1), -(base + 3)])
        clauses.append([-(base + 2), -(base + 3)])

    for edge in edges:
        u, v = edge
        for c in range(3):
            clauses.append([-(3 * u + c + 1), -(3 * v + c + 1)])

    return {"num_vars": num_vars, "clauses": clauses}

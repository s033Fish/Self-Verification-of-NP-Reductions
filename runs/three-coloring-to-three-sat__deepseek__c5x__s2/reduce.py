"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For a graph with n vertices we use 3 variables per vertex:
    x[v][c]  (1-indexed variable number 3*v + c + 1)
meaning "vertex v has colour c" for c in {0, 1, 2}.

We also use one extra padding variable p = 3*n + 1.

Clauses:
  * For every vertex v:            (x[v][0] or x[v][1] or x[v][2])
        -> every vertex gets at least one colour.
  * For every vertex v, c < d:     (~x[v][c] or ~x[v][d] or p)
                                   (~x[v][c] or ~x[v][d] or ~p)
        -> at most one colour per vertex.  The two clauses together are
           equivalent to the 2-literal clause (~x[v][c] or ~x[v][d]),
           because p and ~p cannot both be satisfied.
  * For every edge (u, v), colour c:
                                   (~x[u][c] or ~x[v][c] or p)
                                   (~x[u][c] or ~x[v][c] or ~p)
        -> the endpoints of an edge do not share a colour.  Again the pair
           is equivalent to the 2-literal clause (~x[u][c] or ~x[v][c]).

Every clause has exactly 3 literals on 3 distinct variables, so the result
is a valid 3-SAT instance.  The padding variable is shared by all padded
clauses, which is harmless: for each padded pair, one of the two clauses
contains p and the other ~p, so the pair is satisfied for every value of p
exactly when the underlying 2-literal clause is satisfied.

The construction is a bijection between valid 3-colourings and satisfying
assignments (restricted to the x variables), hence preserves the answer.
It uses O(n^2 + |E|) variables/clauses and runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Variable 3*v + c + 1 represents "vertex v has colour c".
    def x(v, c):
        return 3 * v + c + 1

    pad = 3 * n + 1  # shared padding variable

    clauses = []

    for v in range(n):
        # At least one colour.
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])
        # At most one colour.
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-x(v, c), -x(v, d), pad])
                clauses.append([-x(v, c), -x(v, d), -pad])

    for u, v in edges:
        for c in range(3):
            clauses.append([-x(u, c), -x(v, c), pad])
            clauses.append([-x(u, c), -x(v, c), -pad])

    return {"num_vars": 3 * n + 1, "clauses": clauses}

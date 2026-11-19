"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding
--------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} we introduce a
Boolean variable

    x(v, c) = 3*v + c + 1          (variables are 1..3n)

with the intended meaning "vertex v receives colour c".

Clauses
-------
1. For each vertex v:  [x(v,0), x(v,1), x(v,2)]
   (every vertex gets at least one colour)

2. For each vertex v and each pair of distinct colours c < d:
       [-x(v,c), -x(v,d)]
   (every vertex gets at most one colour; together with (1) exactly one)

3. For each edge {u, v} and each colour c:
       [-x(u,c), -x(v,c)]
   (the two endpoints of an edge do not share a colour)

A satisfying assignment of the formula is exactly a proper 3-colouring of the
graph, and vice versa, so the formula is satisfiable iff the graph is
3-colourable.  The construction uses O(n + |E|) variables/clauses and runs in
polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        return 3 * v + c + 1

    clauses = []

    # (1) at least one colour per vertex
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # (2) at most one colour per vertex
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-var(v, c), -var(v, d)])

    # (3) adjacent vertices differ
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

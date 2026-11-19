"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Target instance (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} we introduce a
boolean variable x[v, c], meaning "vertex v receives colour c".  Numbering
the variables 1..3n:

    var(v, c) = 3 * v + c + 1

Clauses:

1. For each vertex v, the clause
       [ x[v,0], x[v,1], x[v,2] ]
   forces v to receive at least one colour.

2. For each edge [u, v] and each colour c, the clause
       [ -x[u,c], -x[v,c] ]
   forbids u and v from sharing colour c.

A satisfying assignment of the formula therefore selects, for every vertex,
at least one colour, and no edge has both endpoints of the same colour.
Conversely, any proper 3-colouring of the graph satisfies the formula by
setting exactly the chosen colour of each vertex to true (extra colours may
be set arbitrarily, e.g. false).  Hence the formula is satisfiable iff the
graph is 3-colourable.

The construction uses O(n + |E|) variables/clauses and runs in polynomial
time.  It never calls a solver.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an equisatisfiable SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    def var(vertex, colour):
        # Variables are numbered 1..3n.
        return 3 * vertex + colour + 1

    # Every vertex must get at least one of the three colours.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

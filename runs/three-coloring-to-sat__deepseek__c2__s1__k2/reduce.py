"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding
--------
For a graph with vertices 0..n-1 and 3 colours 0,1,2, introduce one Boolean
variable x_{v,c} for every vertex v and colour c, encoded as the integer

    var(v, c) = 3*v + c + 1        (so variables are 1..3n)

meaning "vertex v receives colour c".

Clauses
-------
* For every vertex v:  (x_{v,0} or x_{v,1} or x_{v,2})
  -- v must get at least one colour.
* For every edge [u, v] and every colour c:
      (not x_{u,c} or not x_{v,c})
  -- the two endpoints must not share colour c.

A satisfying assignment of this CNF corresponds exactly to a proper
3-colouring: the vertex clauses force each vertex to have a colour, and the
edge clauses forbid equal colours on adjacent vertices.  Conversely any
proper 3-colouring yields a satisfying assignment.  The construction uses
O(n + |E|) variables/clauses and runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        return 3 * v + c + 1

    clauses = []

    # Each vertex gets at least one of the three colours.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]} with vertices 0..n-1.
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}.

Construction
------------
Introduce a boolean variable x[v][c] for every vertex v in 0..n-1 and every
colour c in {0, 1, 2}, meaning "vertex v receives colour c".  Index them as

    var(v, c) = 3 * v + c + 1        (so variables are 1..3n)

and add the following clauses:

1. For each vertex v:  (x[v][0] or x[v][1] or x[v][2])
   -- every vertex gets at least one colour.

2. For each vertex v and each pair of distinct colours c < d:
       (not x[v][c] or not x[v][d])
   -- every vertex gets at most one colour.

3. For each edge [u, v] and each colour c:
       (not x[u][c] or not x[v][c])
   -- adjacent vertices do not share a colour.

A satisfying assignment of the formula is exactly a proper 3-colouring of
the graph: clauses (1) and (2) pick a unique colour per vertex, and clauses
(3) make every edge properly coloured.  Conversely any proper 3-colouring
extends to a satisfying assignment.  The construction uses O(n + |E|)
variables and clauses, hence runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n

    def var(vertex, colour):
        return 3 * vertex + colour + 1

    clauses = []

    for v in range(n):
        # At least one colour for vertex v.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # At most one colour for vertex v.
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    for u, v in edges:
        for c in range(3):
            # Endpoints of an edge must not share a colour.
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

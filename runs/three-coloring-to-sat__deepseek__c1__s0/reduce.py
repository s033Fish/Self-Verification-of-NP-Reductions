"""Polynomial-time reduction from 3-Coloring to SAT.

A 3-Coloring instance is {"n": n, "edges": [[u, v], ...]}.
A SAT instance is {"num_vars": m, "clauses": [[literal, ...], ...]}.

Construction
------------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2} introduce a
boolean variable x(v, c), numbered 3*v + c + 1.  The variable is true iff
vertex v receives colour c.  There are 3*n variables.

Clauses:
  * For each vertex v, the clause [x(v,0), x(v,1), x(v,2)] says v gets at
    least one colour.
  * For each vertex v and each pair of distinct colours c < c', the clause
    [-x(v,c), -x(v,c')] says v does not get both colours.  Together with the
    previous clauses this forces exactly one colour per vertex.
  * For each edge [u, v] and each colour c, the clause [-x(u,c), -x(v,c)]
    says u and v cannot share colour c.

Correctness
-----------
A proper 3-colouring of the graph assigns exactly one colour to each vertex
and different colours to edge endpoints, so setting x(v,c) true iff v has
colour c satisfies every clause.

Conversely, any satisfying assignment gives each vertex at least one colour
and at most one colour, hence exactly one colour.  The edge clauses ensure
that adjacent vertices never receive the same colour, so the assignment is a
proper 3-colouring.

The construction uses O(n + |E|) variables and clauses and is therefore
polynomial in the size of the input.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an equisatisfiable SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def var(vertex, colour):
        return 3 * vertex + colour + 1

    num_vars = 3 * n
    clauses = []

    for v in range(n):
        # At least one colour for v.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        # At most one colour for v.
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

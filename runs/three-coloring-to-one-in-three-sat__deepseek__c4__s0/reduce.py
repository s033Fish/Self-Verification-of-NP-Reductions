"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x(v, c) meaning "vertex v receives colour c".

  * Exactly-one-colour: for each vertex add the 1-in-3 clause
        [x(v,0), x(v,1), x(v,2)]
    which is true iff the vertex has exactly one colour.

  * Edge constraint: for each edge (u,v) and each colour c add a fresh
    auxiliary variable z(e,c) and the clause
        [x(u,c), x(v,c), z(e,c)]
    A 1-in-3 clause requires exactly one of its three variables to be true.
    If both x(u,c) and x(v,c) were true the clause could not be satisfied
    (already two true), so the clause forbids u and v sharing colour c.
    When at most one of x(u,c), x(v,c) is true, z(e,c) can always be set to
    make exactly one of the three true.  Each z appears in exactly one
    clause, so it never constrains anything else.

A graph is 3-colourable iff the resulting positive 1-in-3 formula is
satisfiable.  The construction uses 3*n + 3*|E| variables and
n + 3*|E| clauses, so it runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-Coloring instance to a 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # x(v, c) -> 3*v + c + 1        (v in 0..n-1, c in 0..2)
    # z(i, c) -> 3*n + 3*i + c + 1  (i = edge index)
    base_z = 3 * n
    num_vars = 3 * n + 3 * len(edges)

    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([3 * v + 1, 3 * v + 2, 3 * v + 3])

    # Forbid the two endpoints of an edge sharing a colour.
    for i, (u, v) in enumerate(edges):
        for c in range(3):
            z = base_z + 3 * i + c + 1
            clauses.append([3 * u + c + 1, 3 * v + c + 1, z])

    return {"num_vars": num_vars, "clauses": clauses}

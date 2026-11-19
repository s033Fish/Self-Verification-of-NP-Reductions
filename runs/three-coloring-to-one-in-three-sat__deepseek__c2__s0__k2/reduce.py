"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v (0-indexed) and colour c in {1,2,3} introduce a boolean
variable x(v,c) = 3*v + c.  The clause

    (x(v,1), x(v,2), x(v,3))

forces exactly one colour to be chosen for v.

For every edge e = (u,v) and every colour c introduce a fresh variable
z(e,c) = 3*n + 3*e + c and the clause

    (x(u,c), x(v,c), z(e,c)).

Because z(e,c) is fresh, this clause is satisfiable for every assignment of
x(u,c), x(v,c) except x(u,c) = x(v,c) = true.  Indeed, if exactly one of the
two is true we set z = false, and if both are false we set z = true.  Thus the
clause enforces NAND(x(u,c), x(v,c)): u and v may not both receive colour c.
The z variables occur nowhere else, so they impose no further constraints.

The resulting formula is satisfiable iff the graph is 3-colourable, and it has
3*n + 3*|E| variables and n + 3*|E| clauses, so the reduction runs in
polynomial time.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses = []

    # Exactly one colour per vertex.
    for v in range(n):
        base = 3 * v
        clauses.append([base + 1, base + 2, base + 3])

    # Forbid the endpoints of every edge from sharing a colour.
    for e, edge in enumerate(edges):
        u, v = edge[0], edge[1]
        for c in range(1, 4):
            xu = 3 * u + c
            xv = 3 * v + c
            z = 3 * n + 3 * e + c
            clauses.append([xu, xv, z])

    return {"num_vars": num_vars, "clauses": clauses}

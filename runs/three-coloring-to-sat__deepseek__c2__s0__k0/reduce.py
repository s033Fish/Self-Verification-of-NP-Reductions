"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding
--------
Given a graph with vertices 0..n-1, introduce three boolean variables per
vertex, one for each colour:

    x[v][c]  is true  iff  vertex v receives colour c.

Number the SAT variables 1..3n via

    var(v, c) = 3*v + c + 1        (v in 0..n-1, c in 0..2)

Clauses
-------
1. At least one colour per vertex:
       (x[v][0] or x[v][1] or x[v][2])            for every vertex v

2. At most one colour per vertex (pairwise exclusion):
       (not x[v][c] or not x[v][d])               for every v and c < d

3. Adjacent vertices must differ:
       (not x[u][c] or not x[v][c])               for every edge {u,v} and colour c

A satisfying assignment of the formula restricts to a proper 3-colouring
of the graph, and every proper 3-colouring extends to a satisfying
assignment (set exactly the chosen colour variable of each vertex true).
The construction uses O(n + m) variables/clauses and runs in polynomial
time.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a SAT instance.

    Parameters
    ----------
    instance : dict
        {"n": n, "edges": [[u, v], ...]} with vertices 0..n-1.

    Returns
    -------
    dict
        {"num_vars": 3*n, "clauses": [[literal, ...], ...]}
    """
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    def var(v, c):
        # Variables are 1..num_vars.
        return 3 * v + c + 1

    # 1. At least one colour for every vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. At most one colour for every vertex.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-var(v, c), -var(v, d)])

    # 3. Endpoints of every edge get different colours.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

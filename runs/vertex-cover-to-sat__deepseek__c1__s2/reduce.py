"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction uses one Boolean variable x_v for each vertex v (encoded as
variable v+1), with an edge clause (x_u OR x_v) for every edge.  The
"at most k vertices" condition is encoded with Sinz's sequential counter,
which uses O(n*k) auxiliary variables and clauses.  Since k < n in the
non-trivial branch, the whole construction is polynomial in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover of negative size exists -> unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Edge clauses: every edge must have at least one chosen endpoint.
    clauses = [[u + 1, v + 1] for u, v in edges]

    # k >= n: choosing all vertices is a valid cover, so the edge clauses
    # alone are always satisfiable (set every x_v true).
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # k == 0: no vertex may be chosen.
    if k == 0:
        clauses.extend([[-v] for v in range(1, n + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Now 1 <= k < n.  Auxiliary variable s(i, j) means "at least j of
    # x_1..x_i are true", for 1 <= i <= n-1 and 1 <= j <= k.
    num_vars = n + (n - 1) * k

    def s(i, j):
        return n + (i - 1) * k + j

    # x_i -> s(i, 1)
    for i in range(1, n):
        clauses.append([-i, s(i, 1)])

    # s(i-1, j) -> s(i, j)
    for i in range(2, n):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # x_i and s(i-1, j-1) -> s(i, j)
    for i in range(2, n):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])

    # x_i and s(i-1, k) cannot both hold: that would mean k+1 chosen vertices.
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

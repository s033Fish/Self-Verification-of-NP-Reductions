"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph with n vertices, introduce a boolean variable x[v][i] for every
vertex v in 0..n-1 and every position i in 0..n-1, meaning "vertex v is the
i-th vertex of the Hamiltonian path".

Variables are numbered 1..n*n with x(v, i) = v*n + i + 1.

Clauses:
  * At least one vertex per position:  (x[0][i] or ... or x[n-1][i])
  * At least one position per vertex:  (x[v][0] or ... or x[v][n-1])
  * At most one vertex per position:   (-x[u][i] or -x[v][i]) for u < v
  * At most one position per vertex:   (-x[v][i] or -x[v][j]) for i < j
  * Adjacency: for i in 0..n-2 and every non-edge {u, v} (u != v):
        (-x[u][i] or -x[v][i+1])   and   (-x[v][i] or -x[u][i+1])

The first four families force the x's to describe a permutation of the
vertices; the last family forces consecutive vertices in that permutation to
be joined by an edge.  Hence a satisfying assignment is exactly a Hamiltonian
path (the endpoints are free, as required).

Edge cases:
  * n = 0: the empty graph has no Hamiltonian path.  Return an unsatisfiable
    formula (a single empty clause) over 0 variables.
  * n = 1: one variable, satisfiable -> yes.
  * n = 2: satisfiable iff the edge {0, 1} is present.

The formula has n^2 variables and O(n^3) clauses, so the reduction is
polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path: emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    num_vars = n * n

    def var(v, i):
        return v * n + i + 1

    # Adjacency lookup for the undirected graph.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    clauses = []

    # Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Each vertex occupies at least one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Each vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Consecutive positions must be connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and not adj[u][v]:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": num_vars, "clauses": clauses}

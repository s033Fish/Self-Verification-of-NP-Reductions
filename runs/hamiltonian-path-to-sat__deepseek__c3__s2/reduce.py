"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph with n vertices we introduce n*n boolean variables

    x[v][i]   (1-based variable index v*n + i + 1)

with the intended meaning "vertex v is the i-th vertex of the path"
(positions 0 .. n-1).

Clauses:

1. every position holds at least one vertex:
       [x[0][i], ..., x[n-1][i]]                       for each i
2. every vertex occurs at least once:
       [x[v][0], ..., x[v][n-1]]                       for each v
3. a vertex occurs at most once:
       [-x[v][i], -x[v][j]]                            for each v, i < j
4. a position holds at most one vertex:
       [-x[u][i], -x[v][i]]                            for each i, u < v
5. consecutive positions are joined by an edge:
       [-x[u][i], -x[v][i+1]]                          for each i < n-1
       and every ordered pair (u, v), u != v, with no edge {u, v}

Clauses 1-4 force the variables to describe a permutation of the vertices
over the positions; clause 5 forces every consecutive pair to be an edge,
i.e. a Hamiltonian path.  Conversely any Hamiltonian path yields the
obvious satisfying assignment.  The formula has O(n^2) variables and
O(n^3) clauses, so the reduction is polynomial.

Edge cases: n = 0 has no Hamiltonian path, so we emit the trivially
unsatisfiable formula {num_vars: 0, clauses: [[]]}.  n = 1 and n = 2 are
handled correctly by the general construction.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no path exists -> return an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        # Variables are 1-based; v in 0..n-1, i in 0..n-1.
        return v * n + i + 1

    # Adjacency set for fast "is there an edge" queries.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    clauses = []

    # 1. Every position has at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Every vertex appears at least once.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 3. A vertex appears at most once (at most one position per vertex).
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. A position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 5. Consecutive positions must be connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in adjacent:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

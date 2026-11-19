"""Polynomial-time reduction from Hamiltonian Path to SAT.

Given an undirected graph G = (V, E) with V = {0, ..., n-1}, introduce a
boolean variable x[v][i] for every vertex v and position i (0 <= i < n),
meaning "vertex v is the i-th vertex of the path".

The CNF below enforces:
  * exactly one vertex per position (at-least-one + at-most-one clauses),
  * every vertex is used at most once,
  * consecutive positions hold adjacent vertices (non-edges are forbidden).

Together these say that the n positions spell out a Hamiltonian path, so
the formula is satisfiable exactly when G has a Hamiltonian path.

The construction uses O(n^2) variables and O(n^3) clauses, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n == 0: no Hamiltonian path exists, so emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Variable var(v, i) is true iff vertex v occupies position i.
    # They are numbered 1 .. n*n.
    def var(v, i):
        return v * n + i + 1

    clauses = []

    # 1. At least one vertex at each position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. At most one vertex at each position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. Each vertex appears at most once (across all positions).
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. Consecutive positions must be joined by an edge.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v) if u < v else (v, u))
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                key = (u, v) if u < v else (v, u)
                if key not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

Encoding: for a graph with n >= 3 vertices introduce a boolean variable
x[v, i] meaning "vertex v is the i-th vertex of the cycle" (positions are
taken modulo n).  The CNF enforces:

  * every position holds at least one vertex;
  * no position holds two different vertices;
  * no vertex occupies two different positions;
  * whenever u is at position i and v at position i+1 (mod n), the edge
    {u, v} must exist.

A satisfying assignment is exactly a cyclic ordering of all vertices along
graph edges, i.e. a Hamiltonian cycle.  Graphs with n <= 2 are always no,
so they are reduced to the unsatisfiable formula with a single empty clause.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph needs at least 3 vertices to contain a cycle.
    if n < 3:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        # Variables are 1..n*n.
        return v * n + i + 1

    clauses = []

    # Every position has at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Every position has at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Every vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Consecutive vertices must be joined by an edge.
    adjacent = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacent[u][v] = True
        adjacent[v][u] = True

    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u != v and not adjacent[u][v]:
                    clauses.append([-var(u, i), -var(v, nxt)])

    return {"num_vars": n * n, "clauses": clauses}

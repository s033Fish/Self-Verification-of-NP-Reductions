"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For a graph with n >= 3 vertices we use the classic positional encoding.
Introduce a boolean variable x[v][i] (1-indexed) meaning "vertex v is the
i-th vertex of the cycle", for v in 0..n-1 and i in 0..n-1.

Clauses:
  * At least one vertex per position:  (x[0][i] or ... or x[n-1][i])
  * At most one vertex per position:   (~x[u][i] or ~x[v][i]) for u < v
  * At least one position per vertex:  (x[v][0] or ... or x[v][n-1])
  * At most one position per vertex:   (~x[v][i] or ~x[v][j]) for i < j
  * Adjacency of consecutive cyclic positions: for every i, every ordered
    pair (u, v), u != v, such that {u, v} is NOT an edge, add
    (~x[u][i] or ~x[v][(i+1) mod n]).

A satisfying assignment is exactly a cyclic ordering of all vertices where
every consecutive pair is an edge, i.e. a Hamiltonian cycle.  Conversely a
Hamiltonian cycle yields a satisfying assignment by listing its vertices in
order (any rotation).

Edge cases: n <= 2 can never have a Hamiltonian cycle, so we return the
unsatisfiable formula containing the empty clause.  n = 3 works with the
general encoding (yes only for the triangle).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph needs at least 3 vertices to contain a cycle.
    if n < 3:
        return {"num_vars": 0, "clauses": [[]]}

    # Adjacency set for O(1) lookups.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    # Variable index (1-based) for "vertex v is at position i".
    def var(v, i):
        return v * n + i + 1

    clauses = []

    # Exactly one vertex per position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])  # at least one
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])  # at most one

    # Exactly one position per vertex.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])  # at least one
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])  # at most one

    # Consecutive positions must be joined by an edge.
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in adjacent:
                    clauses.append([-var(u, i), -var(v, nxt)])

    return {"num_vars": n * n, "clauses": clauses}

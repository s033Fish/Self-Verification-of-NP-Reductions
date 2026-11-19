"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
Let n be the number of vertices.  For n >= 3 we introduce a boolean
variable x[v][i] (1-based index v*n + i + 1) meaning "vertex v is the i-th
vertex of the cycle" for i in 0..n-1.

Clauses:
  * x[0][0]                              (fix vertex 0 at position 0)
  * for each position i:  OR_v x[v][i]   (every position is occupied)
  * for each vertex v and i<j: ~x[v][i] or ~x[v][j]   (vertex used <= once)
  * for each position i and u<v: ~x[u][i] or ~x[v][i] (position holds <= one)
  * for each position i, j=(i+1)%n and every ordered non-adjacent pair
    (a,b): ~x[a][i] or ~x[b][j]         (consecutive vertices are adjacent)

Together these say the x's form a cyclic ordering of all n vertices where
consecutive vertices are adjacent, i.e. a Hamiltonian cycle.

For n <= 2 a Hamiltonian cycle never exists, so we emit an unsatisfiable
formula (a single empty clause over zero variables).
"""

from __future__ import annotations


def _var(v: int, i: int, n: int) -> int:
    """1-based SAT variable for 'vertex v is at position i'."""
    return v * n + i + 1


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # No simple graph with n <= 2 vertices has a cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    adjacent = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacent[u][v] = True
        adjacent[v][u] = True

    clauses: list[list[int]] = []

    # Fix vertex 0 at position 0 (breaks the rotational symmetry).
    clauses.append([_var(0, 0, n)])

    # Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([_var(v, i, n) for v in range(n)])

    # Each vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(u, i, n), -_var(v, i, n)])

    # Consecutive positions must be joined by an edge.
    for i in range(n):
        j = (i + 1) % n
        for a in range(n):
            for b in range(n):
                if a != b and not adjacent[a][b]:
                    clauses.append([-_var(a, i, n), -_var(b, j, n)])

    return {"num_vars": n * n, "clauses": clauses}

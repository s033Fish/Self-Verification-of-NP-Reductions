"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph with n >= 1 vertices we introduce variables

    x[v][i]  (1-based index v*n + i + 1)   for 0 <= v < n, 0 <= i < n

with the intended meaning "vertex v is the i-th vertex of the path".

Clauses:
  (1) For every position i: at least one vertex occupies it.
  (2) For every vertex v: v occurs somewhere.
  (3) For every position i and u < v: not both u and v at position i.
  (4) For every vertex v and i < j: v is not at two positions.
  (5) For every 0 <= i < n-1 and every ordered pair (u, v), u != v, that
      is NOT an edge: not (u at i and v at i+1).

(1)-(4) say the assignment is a bijection positions <-> vertices, i.e. a
permutation of the vertices.  (5) says consecutive vertices of that
permutation are joined by an edge, i.e. the permutation is a Hamiltonian
path.  Hence the formula is satisfiable iff the graph has a Hamiltonian
path.

n = 0 has no Hamiltonian path, so it is mapped to the unsatisfiable
formula with no variables and one empty clause.  n = 1 is handled by the
general encoding (it yields the trivially satisfiable formula with the
single variable x[0][0]).
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no path exists -> unsatisfiable formula (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Adjacency matrix.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    clauses: list[list[int]] = []

    # (1) every position is occupied by at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # (2) every vertex occurs at least once
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # (3) at most one vertex per position
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # (4) each vertex at most once
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # (5) consecutive positions must be adjacent
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and not adj[u][v]:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

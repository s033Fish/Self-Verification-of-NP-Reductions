"""Polynomial-time reduction from Hamiltonian Path (undirected) to SAT.

Encoding
--------
For a graph with n >= 2 vertices we introduce a boolean variable x[v][i]
(true iff vertex v is the i-th vertex of the Hamiltonian path, positions
0..n-1).  Variable number for (v, i) is  v*n + i + 1  (variables 1..n^2).

Clauses:
  A. each position holds at least one vertex:  (x[0][i] v ... v x[n-1][i])
  B. each vertex is used at least once:        (x[v][0] v ... v x[v][n-1])
  C. at most one vertex per position:          (~x[u][i] v ~x[v][i]) for u<v
  D. at most one position per vertex:          (~x[v][i] v ~x[v][j]) for i<j
  E. consecutive positions must be adjacent:   for i in 0..n-2 and every
     non-edge {u,v}: (~x[u][i] v ~x[v][i+1]) and (~x[v][i] v ~x[u][i+1])

A..D force the x to describe a permutation of the vertices; E forces every
consecutive pair to be an edge, i.e. a Hamiltonian path.  Conversely any
Hamiltonian path yields a satisfying assignment.  The encoding is O(n^2)
variables and O(n^2 + n*|nonedges|) clauses, so polynomial.

Edge cases: n = 0 -> unsatisfiable formula (an empty clause); n = 1 -> the
trivially satisfiable empty formula.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # No Hamiltonian path; emit an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Single vertex is a path; emit the trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v) if u < v else (v, u))

    clauses: list[list[int]] = []

    # A. each position has at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # B. each vertex appears at least once
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # C. at most one vertex per position
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # D. at most one position per vertex
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # E. consecutive positions must be joined by an edge
    for i in range(n - 1):
        for u in range(n):
            for v in range(u + 1, n):
                if (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])
                    clauses.append([-var(v, i), -var(u, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

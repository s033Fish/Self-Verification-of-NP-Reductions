"""Polynomial-time reduction from Hamiltonian Path to SAT.

Variable x_{v,i} (1-indexed var = v*n + i + 1) means "vertex v is the i-th
vertex on the Hamiltonian path" (positions 0..n-1).

Clauses:
  * every position holds at least one vertex
  * every vertex occupies at least one position
  * at most one vertex per position
  * at most one position per vertex
  * for each consecutive position pair (i, i+1), the two chosen vertices
    must be joined by an edge: forbid every non-edge pair.

n = 0 is unsatisfiable (empty clause).
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no Hamiltonian path; emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        return v * n + i + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # Each position has at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Each vertex appears at least once.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # At most one vertex per position.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(u, i), -var(w, i)])

    # At most one position per vertex.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Consecutive positions must be connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for w in range(n):
                if u != w and (u, w) not in edge_set:
                    clauses.append([-var(u, i), -var(w, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

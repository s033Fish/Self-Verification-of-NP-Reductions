"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce a boolean variable

    x[v][i]   (variable index v*n + i + 1)

meaning "vertex v is the i-th vertex of the Hamiltonian cycle"
(positions are taken modulo n, so position n is position 0 again).

Clauses:

1. Every vertex occupies at least one position:
       (x[v][0] or ... or x[v][n-1])                       for each v
2. Every position is occupied by at least one vertex:
       (x[0][i] or ... or x[n-1][i])                       for each i
3. No vertex occupies two positions:
       (~x[v][i] or ~x[v][j])                              for each v, i<j
4. No position holds two vertices:
       (~x[u][i] or ~x[v][i])                              for each i, u<v
5. Consecutive vertices must be joined by an edge.  For every
   non-edge {u,v} and every position i:
       (~x[u][i] or ~x[v][(i+1) mod n])
       (~x[v][i] or ~x[u][(i+1) mod n])

Clauses 1-4 force the x[v][i] to describe a permutation of the vertices
around the n positions.  Clause 5 then guarantees that every consecutive
pair (cyclically) is an edge, i.e. a Hamiltonian cycle.  Conversely a
Hamiltonian cycle satisfies all clauses.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they are mapped
to the trivially unsatisfiable formula containing the empty clause.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no simple cycle exists -> unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    clauses: list[list[int]] = []

    # 1. each vertex at least one position
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 2. each position at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 3. each vertex at most one position
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. each position at most one vertex
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 5. consecutive positions must be connected by an edge
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) in edge_set:
                continue
            for i in range(n):
                j = (i + 1) % n
                clauses.append([-var(u, i), -var(v, j)])
                clauses.append([-var(v, i), -var(u, j)])

    return {"num_vars": n * n, "clauses": clauses}

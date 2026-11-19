"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n vertices, introduce a boolean variable

    x[v][i]   meaning "vertex v is the i-th vertex of the Hamiltonian cycle"

for every vertex v in 0..n-1 and every position i in 0..n-1.
Variables are numbered 1..n*n, with x(v, i) = v*n + i + 1.

Clauses:
  * For every position i, at least one vertex sits there:
        (x[0][i] or x[1][i] or ... or x[n-1][i])
  * For every position i and every pair u < v, at most one vertex sits there:
        (~x[u][i] or ~x[v][i])
  * For every vertex v and every pair of positions i < j, v appears at most
    once:
        (~x[v][i] or ~x[v][j])
  * For every position i and every ordered pair (u, v), u != v, such that
    {u, v} is NOT an edge of the graph, u and v cannot occupy consecutive
    positions i and (i+1) mod n:
        (~x[u][i] or ~x[v][(i+1) mod n])

Together the first three groups force a bijection between vertices and
positions (n positions each holding at least one of n vertices, each vertex
used at most once), and the last group forces consecutive positions to be
joined by an edge, i.e. a Hamiltonian cycle.

Edge cases: a simple graph needs at least 3 vertices for a cycle, so for
n <= 2 we return the unsatisfiable formula {"num_vars": 0, "clauses": [[]]}.
For n >= 3 the encoding above is exact.

The construction uses O(n^3) clauses, so it runs in polynomial time.
"""

from __future__ import annotations


def _unsat() -> dict:
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2 can never have a Hamiltonian cycle.
    if n <= 2:
        return _unsat()

    edge_set = {frozenset((u, v)) for u, v in edges}

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    clauses: list[list[int]] = []

    # 1. Every position holds at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Every position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. Every vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. Consecutive positions must be joined by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])

    return {"num_vars": n * n, "clauses": clauses}

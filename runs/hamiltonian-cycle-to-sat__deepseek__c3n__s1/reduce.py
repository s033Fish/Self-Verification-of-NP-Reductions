"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce n*n boolean variables

    x[v][i]   (1-indexed as v*n + i + 1)

with the intended meaning "vertex v is the i-th vertex of the cycle"
(positions are 0 .. n-1, and position n-1 is adjacent back to position 0).

Clauses:
  * each vertex occupies at least one position
  * each vertex occupies at most one position
  * each position holds at least one vertex
  * each position holds at most one vertex
  * for every ordered pair (u, v) that is NOT an edge and every position i,
    forbid u at i together with v at (i+1) mod n

The first four groups force a bijection between vertices and positions; the
last group forces consecutive positions to be joined by an edge, i.e. a
Hamiltonian cycle.

Graphs with n <= 2 are always no (no simple cycle), so we return the
unsatisfiable formula {num_vars: 0, clauses: [[]]}.

The number of clauses is O(n^3) and the number of variables is O(n^2), so
the reduction runs in polynomial time.
"""

from __future__ import annotations

from problems import HamiltonianCycle, Sat


def reduce(instance):
    HamiltonianCycle.validate(instance)

    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: a simple graph cannot contain a cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def var(vertex: int, pos: int) -> int:
        return vertex * n + pos + 1

    num_vars = n * n
    clauses = []

    # Every vertex appears in at least one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # Every vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Every position is filled by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Every position is filled by at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Consecutive positions must be joined by an edge.
    for u in range(n):
        for v in range(n):
            if u != v and (u, v) not in edge_set:
                for i in range(n):
                    clauses.append([-var(u, i), -var(v, (i + 1) % n)])

    result = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(result)
    return result

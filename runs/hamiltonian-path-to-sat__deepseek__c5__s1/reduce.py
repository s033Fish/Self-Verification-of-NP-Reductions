"""Polynomial-time reduction from Hamiltonian Path to SAT.

Idea
----
For a graph with n >= 1 vertices, introduce a boolean variable

    x[v][i]   meaning "vertex v is the i-th vertex of the Hamiltonian path"

for v in 0..n-1 and i in 0..n-1.  Variable number is v*n + i + 1.

The formula enforces:

  * every position holds at least one vertex,
  * every vertex appears in at least one position,
  * no vertex appears in two positions,
  * no position holds two vertices,
  * consecutive positions are joined by an edge of the graph.

The first four families make x a bijection between vertices and positions,
i.e. a permutation; the last family forces consecutive vertices of that
permutation to be adjacent.  Hence a satisfying assignment exists iff the
graph has a Hamiltonian path.

Edge cases:
  * n = 0: no Hamiltonian path.  We emit the unsatisfiable formula with no
    variables and a single empty clause.
  * n = 1: the single vertex is a path; the formula is trivially satisfiable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: unsatisfiable (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses: list[list[int]] = []

    # 1. Each position contains at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Each vertex appears in at least one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 3. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. Each position contains at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 5. Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(u + 1, n):
                if (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])
                    clauses.append([-var(v, i), -var(u, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

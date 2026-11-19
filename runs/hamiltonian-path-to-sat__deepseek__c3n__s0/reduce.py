"""Polynomial-time reduction from Hamiltonian Path (undirected) to SAT.

Encoding (order / position based):
    variable x[v][i]  (1-indexed) is true iff vertex v is the i-th vertex
    of the Hamiltonian path, for v in 0..n-1 and i in 0..n-1.

Clauses:
  * Every position holds at least one vertex:
        [x[0][i], x[1][i], ..., x[n-1][i]]        for each i
  * No vertex occurs twice:
        [-x[v][i], -x[v][j]]                      for each v, i < j
  * No position holds two vertices:
        [-x[u][i], -x[v][i]]                      for each i, u < v
  * Consecutive positions must be joined by an edge:
        [-x[u][i], -x[v][i+1]]   for each i < n-1 and each non-edge {u,v}

Together the first three clause families force a bijection between the n
vertices and the n positions, and the last family forces consecutive
vertices to be adjacent, i.e. exactly a Hamiltonian path.

Edge cases:
  * n = 0 -> no.  We emit num_vars=0 and one empty clause [], unsatisfiable.
  * n = 1 -> yes.  Single variable x[0][0] and clause [1].
  * n = 2 -> yes iff edge [0,1] present (handled by the non-edge clauses).

The formula has O(n^2) variables and O(n^3) clauses, so the reduction runs
in polynomial time.
"""

from __future__ import annotations

from typing import Any


def _var(v: int, i: int, n: int) -> int:
    """1-indexed SAT variable for 'vertex v is at position i'."""
    return v * n + i + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no path exists; emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    num_vars = n * n
    clauses: list[list[int]] = []

    # 1) Each position has at least one vertex.
    for i in range(n):
        clauses.append([_var(v, i, n) for v in range(n)])

    # 2) Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # 3) Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(u, i, n), -_var(v, i, n)])

    # 4) Consecutive positions must be connected by an edge.
    edge_set = {frozenset((u, v)) for u, v in edges}
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-_var(u, i, n), -_var(v, i + 1, n)])

    return {"num_vars": num_vars, "clauses": clauses}

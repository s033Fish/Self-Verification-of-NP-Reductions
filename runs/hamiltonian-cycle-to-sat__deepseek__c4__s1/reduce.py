"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

Encoding: variable x_{v,i} (1-indexed) means "vertex v is the i-th vertex
visited on the tour", for v, i in 0..n-1.

Constraints:
  * every position holds at least one vertex
  * every vertex appears at least once
  * no vertex appears twice, no position holds two vertices
  * consecutive positions (including the wrap-around pair) must be joined
    by an edge of the graph

For n <= 2 there is no Hamiltonian cycle, so we emit an unsatisfiable
formula (a single empty clause with zero variables).
"""

from __future__ import annotations


def _var(v: int, i: int, n: int) -> int:
    """1-indexed SAT variable for 'vertex v is at position i'."""
    return v * n + i + 1


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no simple cycle can visit every vertex.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses: list[list[int]] = []

    # Each position has at least one vertex.
    for i in range(n):
        clauses.append([_var(v, i, n) for v in range(n)])

    # Each vertex appears at least once.
    for v in range(n):
        clauses.append([_var(v, i, n) for i in range(n)])

    # Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(u, i, n), -_var(v, i, n)])

    # Consecutive positions must be adjacent in the graph.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-_var(u, i, n), -_var(v, i + 1, n)])
    # Wrap-around from last position back to first.
    for u in range(n):
        for v in range(n):
            if u != v and (u, v) not in edge_set:
                clauses.append([-_var(u, n - 1, n), -_var(v, 0, n)])

    return {"num_vars": n * n, "clauses": clauses}

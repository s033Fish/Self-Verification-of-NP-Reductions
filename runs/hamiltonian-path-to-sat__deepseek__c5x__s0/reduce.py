"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph with n >= 2 vertices we introduce n*n boolean variables

    p(i, v)   meaning "vertex v is the i-th vertex of the path"

numbered 1..n*n as  var(i, v) = i*n + v + 1  (i, v in 0..n-1).

Clauses:
  * for every position i:      (p(i,0) v ... v p(i,n-1))
        -> every position is occupied by at least one vertex
  * for every i < j and v:     (~p(i,v) v ~p(j,v))
        -> a vertex occupies at most one position
  * for every i and u < v:     (~p(i,u) v ~p(i,v))
        -> a position holds at most one vertex
  * for every i in 0..n-2 and every ordered pair u != v with
    {u, v} not an edge:        (~p(i,u) v ~p(i+1,v))
        -> consecutive path vertices must be joined by an edge

Together the first three clause families force a bijection between
positions 0..n-1 and vertices, and the last family forces consecutive
vertices to be adjacent, i.e. a Hamiltonian path.  Conversely any
Hamiltonian path yields a satisfying assignment.

Edge cases:
  n = 0 -> unsatisfiable formula (the empty clause)
  n = 1 -> satisfiable formula (no clauses)
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """Variable index (1-based) for 'vertex v is at position i'."""
    return i * n + v + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no path exists -> return an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n = 1: the single vertex is a path -> satisfiable formula.
    if n == 1:
        return {"num_vars": 0, "clauses": []}

    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: list[list[int]] = []

    # Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([_var(i, v, n) for v in range(n)])

    # Each vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # Consecutive vertices must be adjacent.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in edge_set:
                    clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])

    return {"num_vars": n * n, "clauses": clauses}

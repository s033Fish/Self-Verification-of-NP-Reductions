"""Polynomial-time reduction from Hamiltonian Path to SAT.

SOURCE: HamiltonianPath instance {"n": n, "edges": [[u, v], ...]}
TARGET: Sat instance {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For n >= 2 we introduce a boolean variable x(i, v) for every position
i in 0..n-1 and every vertex v in 0..n-1, meaning "vertex v is the i-th
vertex of the path".  Variable number: i*n + v + 1.

Clauses:
  * each position holds at least one vertex:   (x(i,0) v ... v x(i,n-1))
  * each position holds at most one vertex:    (~x(i,u) v ~x(i,w)) for u<w
  * each vertex occupies at least one position: (x(0,v) v ... v x(n-1,v))
  * each vertex occupies at most one position:  (~x(i,v) v ~x(j,v)) for i<j
  * consecutive positions are adjacent: for i in 0..n-2 and every
    ordered pair (u,v), u != v, with {u,v} not an edge, add
    (~x(i,u) v ~x(i+1,v)).

A satisfying assignment is exactly a permutation of the vertices in which
every consecutive pair is an edge, i.e. a Hamiltonian path, and vice versa.

Edge cases:
  n = 0 -> unsatisfiable formula (one empty clause).
  n = 1 -> trivially satisfiable formula (no clauses).
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """1-based SAT variable for 'vertex v is at position i'."""
    return i * n + v + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no Hamiltonian path exists.  Emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n = 1: the single vertex is a path.  Emit a trivially satisfiable
    # formula (no clauses, no variables).
    if n == 1:
        return {"num_vars": 0, "clauses": []}

    edge_set: set[frozenset[int]] = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    clauses: list[list[int]] = []

    # 1. Each position has at least one vertex.
    for i in range(n):
        clauses.append([_var(i, v, n) for v in range(n)])

    # 2. Each position has at most one vertex.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, w, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clauses.append([_var(i, v, n) for i in range(n)])

    # 4. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # 5. Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])

    return {"num_vars": n * n, "clauses": clauses}

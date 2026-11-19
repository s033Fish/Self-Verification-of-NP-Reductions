"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

SOURCE: HamiltonianCycle instance {"n": n, "edges": [[u, v], ...]}
TARGET: Sat instance {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
For n >= 3 we introduce a boolean variable x[v][i] meaning "vertex v is the
i-th vertex on the cycle" (positions 0..n-1, indices taken modulo n).

Clauses:
  * every vertex occupies at least one position:
        (x[v][0] or ... or x[v][n-1])          for each v
  * every position is occupied by at least one vertex:
        (x[0][i] or ... or x[n-1][i])          for each i
  * at most one position per vertex:
        (~x[v][i] or ~x[v][j])                 for each v, i < j
  * at most one vertex per position:
        (~x[u][i] or ~x[v][i])                 for each i, u < v
  * consecutive positions must be joined by an edge:
        (~x[u][i] or ~x[v][(i+1) mod n])       for each i and each
                                               ordered non-edge pair u != v

Together the first four families force the x's to encode a permutation of
the vertices; the last family forces consecutive vertices of that cyclic
permutation to be adjacent, i.e. a Hamiltonian cycle.

For n <= 2 no simple graph can have a cycle, so we return the trivially
unsatisfiable formula containing the empty clause.
"""

from __future__ import annotations

from typing import Any


def _var(v: int, i: int, n: int) -> int:
    """Variable index (1-based) for 'vertex v is at position i'."""
    return v * n + i + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: always "no".  Emit an unsatisfiable formula (empty clause).
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: list[list[int]] = []

    # 1. each vertex appears at least once
    for v in range(n):
        clauses.append([_var(v, i, n) for i in range(n)])

    # 2. each position holds at least one vertex
    for i in range(n):
        clauses.append([_var(v, i, n) for v in range(n)])

    # 3. each vertex appears at most once
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # 4. each position holds at most one vertex
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(u, i, n), -_var(v, i, n)])

    # 5. consecutive positions must be adjacent
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-_var(u, i, n), -_var(v, j, n)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Clique to SAT.

Encoding
--------
Given a Clique instance (n, edges, k), introduce a boolean variable
    x[i][v]   (1 <= i <= k, 0 <= v < n)
meaning "the i-th chosen clique vertex is v".

Clauses:
  * for every position i, at least one vertex is chosen:
        (x[i][0] or x[i][1] or ... or x[i][n-1])
  * for every position i and every pair u < v, at most one vertex:
        (-x[i][u] or -x[i][v])
  * for every pair of positions i < j and every vertex u, the two
    positions cannot pick the same vertex (this makes the k vertices
    distinct, which is needed when k > n):
        (-x[i][u] or -x[j][u])
  * for every pair of positions i < j and every non-edge {u, v}:
        (-x[i][u] or -x[j][v]) and (-x[i][v] or -x[j][u])

A satisfying assignment selects, for each position, exactly one distinct
vertex, and every pair of selected vertices is an edge: a clique of size
exactly k.  Conversely any clique of size >= k yields a satisfying
assignment by picking any k of its vertices.  Hence the formula is
satisfiable iff the graph has a clique of at least k vertices.

Edge cases:
  * k <= 0: the answer is always yes; return the empty (satisfiable)
    formula with 0 variables.
  * k > n: the answer is always no; return a formula containing the empty
    clause, which is unsatisfiable.

The reduction uses O(k*n) variables and O(k^2*n^2) clauses, i.e. it runs in
polynomial time in the size of the instance.
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """1-based SAT variable for position i (1-based) and vertex v (0-based)."""
    return (i - 1) * n + v + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: always yes -> trivially satisfiable formula.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: impossible -> unsatisfiable formula (empty clause).
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    num_vars = k * n
    clauses: list[list[int]] = []

    # At least one vertex per position.
    for i in range(1, k + 1):
        clauses.append([_var(i, v, n) for v in range(n)])

    # At most one vertex per position.
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # Distinct vertices across different positions.
    for u in range(n):
        for i in range(1, k + 1):
            for j in range(i + 1, k + 1):
                clauses.append([-_var(i, u, n), -_var(j, u, n)])

    # Non-edges may not be selected by two different positions.
    edge_set = {frozenset(e) for e in edges}
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(u + 1, n):
                    if frozenset((u, v)) not in edge_set:
                        clauses.append([-_var(i, u, n), -_var(j, v, n)])
                        clauses.append([-_var(i, v, n), -_var(j, u, n)])

    return {"num_vars": num_vars, "clauses": clauses}

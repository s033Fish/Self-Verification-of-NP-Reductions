"""Polynomial-time reduction from Clique to SAT.

SOURCE = Clique:  {"n": n, "edges": [[u, v], ...], "k": k}
TARGET = Sat:     {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction idea
--------------
Handle the trivial edge cases directly:

  * k <= 0            -> always yes: return an empty (satisfiable) formula.
  * k >  n            -> always no : return a formula with an empty clause.
  * otherwise 1 <= k <= n: build the standard "k positions" encoding.

For 1 <= k <= n introduce a variable x[i][v] (i in 0..k-1, v in 0..n-1)
meaning "vertex v is the i-th vertex of the clique".  The clauses are:

  1. For every position i:  (x[i][0] or ... or x[i][n-1])
     -> position i is filled by some vertex.
  2. For every position i and every pair v < w:
         (not x[i][v] or not x[i][w])
     -> position i holds at most one vertex.
  3. For every pair of positions i < j and every pair of vertices v, w
     such that v == w or {v, w} is not an edge:
         (not x[i][v] or not x[j][w])
     -> the chosen vertices are pairwise distinct and pairwise adjacent.

A satisfying assignment selects exactly one vertex per position, all
distinct and pairwise adjacent, i.e. a clique of size k.  Conversely any
clique of size >= k contains a clique of size exactly k (k <= n), which
yields a satisfying assignment.  So the formula is satisfiable iff the
graph has a clique of at least k vertices.

The encoding uses k*n variables and O(k^2 * n^2) clauses, so it runs in
polynomial time.
"""

from __future__ import annotations

from typing import Any


def _yes_instance() -> dict[str, Any]:
    """An empty CNF formula: satisfiable (yes)."""
    return {"num_vars": 0, "clauses": []}


def _no_instance() -> dict[str, Any]:
    """A CNF formula containing the empty clause: unsatisfiable (no)."""
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases of the Clique definition.
    if k <= 0:
        return _yes_instance()
    if k > n:
        return _no_instance()

    # Now 1 <= k <= n.  Variable x(i, v) is encoded as i*n + v + 1.
    num_vars = k * n

    def var(i: int, v: int) -> int:
        return i * n + v + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    clauses: list[list[int]] = []

    # 1. Every position is filled by at least one vertex.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # 2. Every position holds at most one vertex.
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. Chosen vertices across positions are distinct and adjacent.
    for i in range(k):
        for j in range(i + 1, k):
            for v in range(n):
                for w in range(n):
                    if v == w or frozenset((v, w)) not in edge_set:
                        clauses.append([-var(i, v), -var(j, w)])

    return {"num_vars": num_vars, "clauses": clauses}

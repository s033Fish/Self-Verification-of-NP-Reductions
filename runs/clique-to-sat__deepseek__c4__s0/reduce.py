"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff there is a set of at least k pairwise-adjacent vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction idea (standard):
  For 1 <= k <= n introduce a variable x[i][v] for each position
  i in 0..k-1 and vertex v in 0..n-1, meaning "the i-th chosen clique
  vertex is v".  Clauses force:
    * each position picks at least one vertex,
    * each position picks at most one vertex,
    * choices in different positions are distinct and joined by an edge.
  A satisfying assignment corresponds exactly to a k-clique.

Edge cases:
  k <= 0  -> always yes  -> trivially satisfiable formula (no clauses).
  k >  n  -> always no   -> unsatisfiable formula (contains empty clause).
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """1-based SAT variable for position i choosing vertex v."""
    return i * n + v + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: a clique of size 0 always exists -> satisfiable.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: cannot fit k vertices -> unsatisfiable (empty clause).
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # 1 <= k <= n.
    edge_set = {frozenset((u, v)) for u, v in edges}

    num_vars = k * n
    clauses: list[list[int]] = []

    # 1) Each position i must choose at least one vertex.
    for i in range(k):
        clauses.append([_var(i, v, n) for v in range(n)])

    # 2) Each position i chooses at most one vertex.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # 3) Different positions must use distinct, adjacent vertices.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or frozenset((u, v)) not in edge_set:
                        clauses.append([-_var(i, u, n), -_var(j, v, n)])

    return {"num_vars": num_vars, "clauses": clauses}

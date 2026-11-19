"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT    instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For 1 <= k <= n we use boolean variables x_{i,v} (i in 1..k, v in 0..n-1)
meaning "vertex v is the i-th chosen clique vertex".

Clauses:
  * for every position i: (x_{i,0} or ... or x_{i,n-1})
        -- some vertex sits at position i.
  * for every position i and u < v: (~x_{i,u} or ~x_{i,v})
        -- at most one vertex per position.
  * for every pair of positions i < j and every pair (u, v) that is NOT an
    edge (including u == v): (~x_{i,u} or ~x_{j,v})
        -- chosen vertices are distinct and pairwise adjacent.

A satisfying assignment picks k distinct pairwise-adjacent vertices, i.e. a
clique of size k.  Conversely a clique of size >= k yields one of size k.

Edge cases:
  * k <= 0 : always yes  -> empty formula (satisfiable).
  * k >  n : always no   -> formula containing the empty clause (unsat).
"""

from __future__ import annotations

from typing import Any


def _sat_yes() -> dict:
    # No clauses: trivially satisfiable.
    return {"num_vars": 0, "clauses": []}


def _sat_no() -> dict:
    # One empty clause: can never be satisfied.
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return _sat_yes()
    if k > n:
        return _sat_no()

    # 1 <= k <= n
    # variable index for (position i in 1..k, vertex v in 0..n-1)
    def var(i: int, v: int) -> int:
        return (i - 1) * n + v + 1

    num_vars = k * n

    # adjacency matrix
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    clauses: list[list[int]] = []

    # some vertex at each position
    for i in range(1, k + 1):
        clauses.append([var(i, v) for v in range(n)])

    # at most one vertex per position
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # distinct / adjacent across positions
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(n):
                    if u == v or not adj[u][v]:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

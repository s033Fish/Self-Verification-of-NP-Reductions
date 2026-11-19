"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff the graph has a clique of AT LEAST k vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment satisfies every clause.

Reduction
---------
Edge cases handled directly:
  * k <= 0  -> always yes: emit an empty (trivially satisfiable) formula.
  * k > n   -> always no:  emit a formula containing the empty clause [].

Otherwise 1 <= k <= n.  Introduce boolean variables x(i, v) for
i = 1..k (position in the clique) and v = 0..n-1 (vertex), encoded as
the integer (i-1)*n + (v+1), so num_vars = k*n.  The clauses are:

  1. For every position i: [x(i,0), ..., x(i,n-1)]  (at least one vertex).
  2. For every position i and every pair u < v:
         [-x(i,u), -x(i,v)]                          (at most one vertex).
  3. For every pair of positions i < j and every pair of vertices u, v
     with u == v or {u,v} not an edge:
         [-x(i,u), -x(j,v)]                          (distinct, adjacent).

A satisfying assignment picks exactly one vertex per position (clauses 1
and 2); clause 3 forces the k chosen vertices to be pairwise distinct and
adjacent, i.e. a k-clique.  Conversely any k-clique yields a satisfying
assignment by placing its vertices in the k positions.  Since any clique
of size >= k contains one of size exactly k, this is equivalent to the
"at least k" condition.  The formula has O(k*n + k^2*n^2) clauses and
k*n variables, so the reduction is polynomial time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def _trivial_yes() -> Instance:
    """A formula with no clauses: satisfiable."""
    return {"num_vars": 0, "clauses": []}


def _trivial_no() -> Instance:
    """A formula with an empty clause: unsatisfiable."""
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: Instance) -> Instance:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the Clique definition.
    if k <= 0:
        return _trivial_yes()
    if k > n:
        return _trivial_no()

    # 1 <= k <= n.
    num_vars = k * n

    def var(i: int, v: int) -> int:
        # i in 1..k, v in 0..n-1 -> 1..k*n
        return (i - 1) * n + (v + 1)

    # Adjacency set for quick lookup.
    adjacent = [[False] * n for _ in range(n)]
    for edge in edges:
        u, v = edge
        adjacent[u][v] = True
        adjacent[v][u] = True

    clauses: list[list[int]] = []

    for i in range(1, k + 1):
        # At least one vertex in position i.
        clauses.append([var(i, v) for v in range(n)])
        # At most one vertex in position i.
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(n):
                    # Same vertex twice, or a non-edge, cannot both be chosen.
                    if u == v or not adjacent[u][v]:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

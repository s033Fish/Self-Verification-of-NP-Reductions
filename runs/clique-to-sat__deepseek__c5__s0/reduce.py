"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff there is a set of at least k pairwise-adjacent vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction idea
--------------
If k <= 0 the answer is always yes: return the trivially satisfiable empty
formula (no clauses).

If k > n the answer is always no: return the unsatisfiable formula with a
single empty clause.

Otherwise 1 <= k <= n.  Introduce a boolean variable x[i][v] for every
position i in 0..k-1 and every vertex v in 0..n-1, meaning "vertex v is the
i-th vertex of the clique".  Clauses:

  * For every position i: (x[i][0] or ... or x[i][n-1])   -- some vertex here.
  * For every position i and u < v: (not x[i][u] or not x[i][v])
                                                          -- at most one vertex.
  * For every i < j and vertex v: (not x[i][v] or not x[j][v])
                                                          -- positions distinct.
  * For every i < j and every non-edge {u, v} (u != v):
        (not x[i][u] or not x[j][v]) and (not x[j][u] or not x[i][v])
                                                          -- chosen vertices adjacent.

A satisfying assignment picks k distinct, pairwise adjacent vertices, i.e. a
k-clique.  Conversely any clique of size >= k yields a satisfying assignment
by placing k of its vertices in the k positions.  The formula has
O(k^2 * n^2) clauses, so the reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def _trivial_sat() -> dict[str, Any]:
    """A formula that is always satisfiable."""
    return {"num_vars": 0, "clauses": []}


def _trivial_unsat() -> dict[str, Any]:
    """A formula that is always unsatisfiable (contains an empty clause)."""
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a SAT instance (answer-preserving)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the Clique definition.
    if k <= 0:
        return _trivial_sat()
    if k > n:
        return _trivial_unsat()

    # 1 <= k <= n.
    num_vars = k * n

    def var(i: int, v: int) -> int:
        """1-based SAT variable for x[i][v]."""
        return i * n + v + 1

    # Set of undirected edges as frozensets.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: list[list[int]] = []

    # Some vertex at each position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Positions must refer to distinct vertices.
    for i in range(k):
        for j in range(i + 1, k):
            for v in range(n):
                clauses.append([-var(i, v), -var(j, v)])

    # Chosen vertices must be pairwise adjacent: forbid non-edges.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(u + 1, n):
                    if frozenset((u, v)) not in edge_set:
                        clauses.append([-var(i, u), -var(j, v)])
                        clauses.append([-var(j, u), -var(i, v)])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Clique (SOURCE) to SAT (TARGET).

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff the graph on vertices 0..n-1 has a clique of at least k vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment of variables 1..m satisfies every clause.

Reduction idea (standard position encoding)
-------------------------------------------
For 1 <= k <= n introduce a variable x[i][v] for every position
i in 0..k-1 and every vertex v in 0..n-1, meaning "the i-th chosen
clique vertex is v".  Number it as  var(i, v) = i*n + v + 1.

Clauses:
  * (x[i][0] or ... or x[i][n-1]) for every i
        -> every position chooses at least one vertex.
  * (-x[i][u] or -x[i][v]) for every i and every u < v
        -> every position chooses at most one vertex.
  * (-x[i][v] or -x[j][v]) for every i < j and every v
        -> the k chosen vertices are pairwise distinct.
  * (-x[i][u] or -x[j][v]) for every i < j and every ordered pair
    (u, v), u != v, with {u, v} not an edge
        -> any two chosen vertices are adjacent.

A satisfying assignment picks exactly one distinct vertex per position,
and all pairs are adjacent, i.e. a k-clique.  Conversely a clique of
size >= k yields a satisfying assignment by putting its first k
vertices in the k positions.  The encoding uses O(k^2 * n^2) clauses
and O(k*n) variables, hence polynomial time.

Edge cases:
  * k <= 0: always yes -> return the trivially satisfiable empty formula.
  * k > n : always no  -> return a formula containing the empty clause.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a Clique instance to a SAT instance (same yes/no answer)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: a clique of at least k vertices always exists.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: impossible to pick k distinct vertices.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n, so n >= 1.
    edge_set = {frozenset(edge) for edge in edges}

    def var(i: int, v: int) -> int:
        return i * n + v + 1

    clauses: list[list[int]] = []

    for i in range(k):
        # At least one vertex in position i.
        clauses.append([var(i, v) for v in range(n)])
        # At most one vertex in position i.
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    for i in range(k):
        for j in range(i + 1, k):
            # Positions i and j must hold distinct vertices.
            for v in range(n):
                clauses.append([-var(i, v), -var(j, v)])
            # Non-adjacent vertices cannot occupy positions i and j.
            for u in range(n):
                for v in range(n):
                    if u != v and frozenset((u, v)) not in edge_set:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": k * n, "clauses": clauses}

"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff the graph on vertices 0..n-1 has a clique of at least k vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment satisfies every clause.

Encoding
--------
For k <= 0 the answer is trivially yes, so return an empty (satisfiable)
formula.

For k > n the answer is trivially no, so return a formula containing the
empty clause (unsatisfiable).

Otherwise (1 <= k <= n) introduce a boolean variable x[i][v] for every
position i in 0..k-1 and vertex v in 0..n-1, meaning "the i-th chosen
clique vertex is v".  Variable number is i*n + v + 1.

Clauses:
  * For each position i: (x[i][0] or ... or x[i][n-1])       -- pick a vertex.
  * For each position i and each pair u < v:
        (not x[i][u] or not x[i][v])                          -- at most one.
  * For each pair of positions i < j and each pair (u, v) that is
    NOT an edge (including u == v):
        (not x[i][u] or not x[j][v])                          -- distinct and
                                                                 adjacent.

A satisfying assignment selects k pairwise-adjacent, distinct vertices,
i.e. a clique of size k; conversely any clique of size >= k yields a
satisfying assignment.  The formula has O(k^2 * n^2) clauses, so the
reduction is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Trivial yes: a clique of size <= 0 always exists.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # Trivial no: cannot choose more than n distinct vertices.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Here 1 <= k <= n, so n >= 1.
    num_vars = k * n

    def var(i: int, v: int) -> int:
        return i * n + v + 1

    # Undirected adjacency set.
    adj: set[tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: list[list[int]] = []

    # At least one vertex per position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Chosen vertices in different positions must be distinct and adjacent.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or (u, v) not in adj:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

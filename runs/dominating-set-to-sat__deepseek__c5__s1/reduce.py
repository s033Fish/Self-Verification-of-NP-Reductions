"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
Variable x_v (v = 0..n-1) is numbered v+1 and means "vertex v is chosen in
the dominating set D".

Domination: for every vertex v we add the clause
    (x_v OR x_u for every neighbour u of v)
so v is either chosen itself or adjacent to a chosen vertex.

Cardinality "at most k": encoded with Sinz's sequential counter, which uses
O(n*k) auxiliary variables s_{i,j} (meaning "at least j of x_1..x_i are
true") and O(n*k) clauses.  This keeps the reduction polynomial.

Special cases:
  * k < 0        -> unsatisfiable formula (single empty clause).
  * k >= n       -> no cardinality constraint is needed.
  * k == 0       -> simply force every x_v to false with unit clauses.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build adjacency (undirected).
    adj: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Domination clauses: x_v OR (x_u for u adjacent to v).
    clauses: list[list[int]] = []
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    # k < 0: always no -> unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: any set of size <= n works, so no cardinality constraint.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # k == 0: force all x_v to be false.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: Sinz sequential counter for "at most k".
    # s(i, j) for i in 1..n, j in 1..k, numbered after the x variables.
    def s(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    # x_i -> s(i, 1)
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    # s(i-1, 1) -> s(i, 1)
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    # x_i AND s(i-1, j-1) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
    # s(i-1, j) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
    # x_i AND s(i-1, k) -> false  (would mean k+1 true variables)
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

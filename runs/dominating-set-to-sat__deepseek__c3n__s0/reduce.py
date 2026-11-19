"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce a boolean variable x_i for every vertex i, meaning "i is in the
dominating set D".  Domination is then a conjunction of clauses, one per
vertex v:

    (x_v OR x_{u1} OR x_{u2} OR ...)   for every neighbour u of v

which says that v itself is chosen or some neighbour of v is chosen.

The remaining requirement is the cardinality constraint |D| <= k, encoded
with the standard sequential (Sinz) counter.  Auxiliary variables s_{i,j}
mean "among x_0..x_i at least j are true".  This uses O(n*k) variables and
clauses, hence polynomial time and size.

Edge cases handled directly:
  * k < 0      -> always no: emit the empty clause [] (unsatisfiable).
  * k >= n     -> always yes: emit the empty CNF (satisfiable).
  * k == 0     -> all x_i must be false (unit clauses) plus domination.
  * n == 0, k >= 0 falls under k >= n and is yes.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- trivial edge cases -------------------------------------------------
    if k < 0:
        # No dominating set of size <= k.  An empty clause is never satisfied.
        return {"num_vars": 0, "clauses": [[]]}

    if k >= n:
        # All n vertices form a dominating set of size n <= k.  Empty CNF is
        # satisfiable (also covers n == 0).
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n, so n >= 1 and k <= n-1.

    # Variable layout: x_i = i + 1 for i in 0..n-1.
    # Auxiliary s_{i,j} = n + i*k + j for i in 0..n-1, j in 1..k.
    num_vars = n + n * k

    def x(i: int) -> int:
        return i + 1

    def s(i: int, j: int) -> int:
        return n + i * k + j

    # Adjacency lists (undirected).
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses: list[list[int]] = []

    # --- domination clauses -------------------------------------------------
    for v in range(n):
        clauses.append([x(v)] + [x(u) for u in adj[v]])

    # --- cardinality constraint |D| <= k ------------------------------------
    if k == 0:
        for i in range(n):
            clauses.append([-x(i)])
        return {"num_vars": num_vars, "clauses": clauses}

    # Sequential counter.
    for i in range(n):
        # x_i -> s_{i,1}
        clauses.append([-x(i), s(i, 1)])

    for i in range(1, n):
        # s_{i-1,1} -> s_{i,1}
        clauses.append([-s(i - 1, 1), s(i, 1)])
        for j in range(2, k + 1):
            # x_i and s_{i-1,j-1} -> s_{i,j}
            clauses.append([-x(i), -s(i - 1, j - 1), s(i, j)])
            # s_{i-1,j} -> s_{i,j}
            clauses.append([-s(i - 1, j), s(i, j)])
        # x_i and s_{i-1,k} cannot both hold (would give k+1 chosen).
        clauses.append([-x(i), -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

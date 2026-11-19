"""Polynomial-time reduction from Dominating Set to SAT.

Source instance:  {"n": n, "edges": [[u, v], ...], "k": k}
Target instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (variable number v+1),
meaning "v is put into the dominating set D".

* Domination is encoded directly: for every vertex v the clause
      (x_v or x_{u1} or ... or x_{ud})
  where u1..ud are the neighbours of v, says that v is either selected or
  adjacent to a selected vertex.

* The cardinality constraint |D| <= k is encoded with Sinz's sequential
  counter (a polynomial-size CNF).  Auxiliary variable s(i, j) means
  "at least j of x_1..x_i are true".  The clauses force s to be true exactly
  when it should be, and the overflow clause (not x_i or not s(i-1, k))
  makes any assignment with more than k true x's unsatisfiable.

Edge cases
----------
* k < 0            -> unsatisfiable formula (one empty clause).
* k >= n           -> the cardinality bound is vacuous (at most n x's can be
                      true), so only the domination clauses are emitted.
* n = 0, k >= 0    -> no clauses at all, which is satisfiable.
* k = 0            -> every x_v is forced false with a unit clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no set of at most k vertices exists -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # x_v is the SAT variable number v + 1.
    clauses: list[list[int]] = []

    # Domination clauses.
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    if k >= n:
        # At most n variables can be true, so |D| <= k is automatic.
        return {"num_vars": n, "clauses": clauses}

    if k == 0:
        # D must be empty: forbid every vertex.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: Sinz sequential counter for "at most k of x_1..x_n".
    # s(i, j)  <=>  at least j of x_1..x_i are true, for 1 <= i <= n, 1 <= j <= k.
    def s(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
    for i in range(2, n + 1):
        # Overflow: x_i true together with k trues among x_1..x_{i-1} is bad.
        clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

SOURCE: DominatingSet  {"n", "edges", "k"}
TARGET: Sat            {"num_vars", "clauses"}

Idea
----
Introduce one boolean variable x_v for every vertex v (literal v+1), meaning
"v is placed in the dominating set D".

1. Domination: for every vertex v the clause
       (x_v OR x_u1 OR ... OR x_ud)
   where u1..ud are the neighbours of v, says that v is dominated (either v
   itself or one of its neighbours is in D).

2. Cardinality "at most k": encoded with Sinz's sequential counter.
   Auxiliary variable s[i][j] (1 <= i <= n, 1 <= j <= k) means
   "at least j of x_1..x_i are true".  The clauses are
       (~x_i OR s[i][1])                       for all i
       (~s[i-1][1] OR s[i][1])                 for i >= 2
       (~x_i OR ~s[i-1][j-1] OR s[i][j])       for i >= 2, j >= 2
       (~s[i-1][j] OR s[i][j])                 for i >= 2, j >= 2
       (~x_i OR ~s[i-1][k])                    for i >= 2
   which is satisfiable exactly when at most k of the x's are true.
   For k = 0 this degenerates to the unit clauses (~x_v).

Edge cases
----------
* k < 0            -> unsatisfiable formula ([[]] with 0 vars).
* k >= n           -> the cardinality constraint is vacuous, so only the
                      domination clauses are emitted.  In particular n = 0
                      yields the empty (satisfiable) formula.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always "no".
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # x_v is literal v+1.
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses: list[list[int]] = []
    for v in range(n):
        clause = [v + 1]
        for u in adj[v]:
            clause.append(u + 1)
        clauses.append(clause)

    # k >= n: at most k is automatic.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # k == 0: every x must be false.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Sequential counter.  s(i, j) is a 1-based literal index.
    base = n

    def s(i: int, j: int) -> int:
        return base + (i - 1) * k + j

    num_vars = n + n * k

    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

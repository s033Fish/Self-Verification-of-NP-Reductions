"""Polynomial-time reduction from Vertex Cover to SAT.

Idea
----
Introduce one Boolean variable per *non-isolated* vertex (a vertex incident to
at least one edge).  Isolated vertices are never useful in a vertex cover, so
dropping them preserves the answer while keeping the number of variables at
most 2 * |edges| -- polynomial in the input length even when ``n`` is huge.
For every edge {u, v} add the clause (x_u OR x_v): a satisfying assignment must
pick at least one endpoint of every edge, i.e. the true x's form a vertex cover.

The "at most k" bound is encoded with Sinz's sequential counter (a polynomial
size encoding) over the non-isolated vertices.  If k >= (number of non-isolated
vertices) the bound is vacuous and no cardinality clauses are needed.  If
k < 0 the instance is always "no", encoded as a single empty clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no: emit an unsatisfiable formula (empty clause).
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Only non-isolated vertices can matter for a vertex cover.
    vertices = sorted({v for edge in edges for v in edge})
    n = len(vertices)
    index = {v: i + 1 for i, v in enumerate(vertices)}

    # Edge clauses: (x_u OR x_v) for each edge.
    clauses: list[list[int]] = [[index[u], index[v]] for (u, v) in edges]

    # If k >= n the at-most-k constraint is vacuous.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # Here 0 <= k < n.  Encode "at most k of x_1..x_n are true".
    if k == 0:
        # No vertex may be selected.
        for v in range(1, n + 1):
            clauses.append([-v])
        return {"num_vars": n, "clauses": clauses}

    # Sinz sequential counter.  Auxiliary variable s_{i,j} (1 <= i <= n-1,
    # 1 <= j <= k) means "at least j of x_1..x_i are true".
    num_aux = (n - 1) * k
    num_vars = n + num_aux

    def sid(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    # (1) x_i -> s_{i,1}
    for i in range(1, n):
        clauses.append([-i, sid(i, 1)])
    # (2) s_{i-1,1} -> s_{i,1}
    for i in range(2, n):
        clauses.append([-sid(i - 1, 1), sid(i, 1)])
    # (3) x_i and s_{i-1,j-1} -> s_{i,j}
    # (4) s_{i-1,j} -> s_{i,j}
    for i in range(2, n):
        for j in range(2, k + 1):
            clauses.append([-i, -sid(i - 1, j - 1), sid(i, j)])
            clauses.append([-sid(i - 1, j), sid(i, j)])
    # (5) x_i -> not s_{i-1,k}   (enforces at most k)
    for i in range(2, n + 1):
        clauses.append([-i, -sid(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

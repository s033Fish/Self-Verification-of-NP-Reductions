"""Polynomial-time reduction from Dominating Set to SAT.

Source instance:  {"n": n, "edges": [[u, v], ...], "k": k}
Target instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (SAT variable v+1),
meaning "v is placed in the dominating set D".

Domination: for every vertex v the clause

    (x_v OR x_{u1} OR x_{u2} OR ...)

over v and all of its neighbours expresses that v is dominated (either v
itself or some neighbour is chosen).  An isolated vertex yields the unit
clause (x_v).

Size bound: |D| <= k is encoded with Sinz's sequential counter, which uses
O(n * k) auxiliary variables and clauses.  Since k >= n makes the instance
trivially yes, we clamp k to min(k, n); hence the encoding is O(n^2),
polynomial in the input length (even though k itself is written in binary).

Edge cases:
  * k < 0            -> unsatisfiable formula (contains the empty clause).
  * n == 0, k >= 0   -> satisfiable formula (no clauses).
  * k >= n           -> always yes; domination clauses alone are satisfiable
                        (pick every vertex), so no cardinality constraint.
  * 0 <= k < n       -> domination clauses + at-most-k counter.
"""

from __future__ import annotations

from typing import Any


def _domination_clauses(n: int, adj: list[list[int]]) -> list[list[int]]:
    """Clause for each vertex: it or one of its neighbours is chosen."""
    clauses: list[list[int]] = []
    for v in range(n):
        clause = [v + 1]
        for u in adj[v]:
            clause.append(u + 1)
        clauses.append(clause)
    return clauses


def _at_most_k_clauses(n: int, k: int, first_aux: int) -> tuple[list[list[int]], int]:
    """Sinz sequential-counter encoding of "at most k of x_1..x_n are true".

    x_i is SAT variable i (i = 1..n).  Auxiliary variables s_{i,j}
    (1 <= i <= n, 1 <= j <= k) mean "at least j of x_1..x_i are true".
    They are numbered consecutively starting at first_aux.

    Returns (clauses, number_of_aux_variables).
    """
    if k <= 0:
        # At most zero true: every x_i must be false.
        return ([[-i] for i in range(1, n + 1)], 0)

    def s(i: int, j: int) -> int:
        # i in 1..n, j in 1..k
        return first_aux + (i - 1) * k + (j - 1)

    clauses: list[list[int]] = []
    # 1. x_i -> s_{i,1}
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    # 2. s_{i-1,1} -> s_{i,1}
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    # 3. x_i and s_{i-1,j-1} -> s_{i,j}
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
    # 4. s_{i-1,j} -> s_{i,j}
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
    # 5. x_i -> not s_{i-1,k}   (would make k+1 true)
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return clauses, n * k


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n == 0 is yes for every k >= 0.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses = _domination_clauses(n, adj)

    # k >= n: always yes, domination clauses are satisfiable by picking all.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 0 <= k < n: add the at-most-k cardinality constraint.
    card_clauses, num_aux = _at_most_k_clauses(n, k, first_aux=n + 1)
    clauses.extend(card_clauses)
    return {"num_vars": n + num_aux, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (meaning "v is in the
dominating set D").  The domination requirement is a plain clause per vertex:

    (x_v OR x_{u1} OR x_{u2} OR ...)      for every neighbour u of v

so that v is either chosen itself or adjacent to a chosen vertex.

The only non-trivial part is the cardinality constraint "|D| <= k".  It is
encoded with Sinz's sequential-counter (unary adder) at-most-k encoding, which
uses O(n*k) auxiliary variables and O(n*k) clauses -- polynomial in the input
size.  Special cases (k < 0, k >= n, n == 0) are handled directly.
"""

from __future__ import annotations


def _unsat():
    # An empty clause can never be satisfied.
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- trivial edge cases -------------------------------------------------
    if k < 0:
        return _unsat()

    # Build adjacency (0-indexed vertices).
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # x_v is variable (v + 1) for v in 0..n-1.
    def x(v):
        return v + 1

    # Domination clauses: every vertex must be dominated.
    clauses = []
    for v in range(n):
        clause = [x(v)] + [x(u) for u in adj[v]]
        clauses.append(clause)

    # If k >= n the cardinality constraint is vacuous; the all-true assignment
    # satisfies every domination clause.  This also covers n == 0.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # --- 0 <= k < n : encode "at most k of x_0..x_{n-1} are true" -----------
    if k == 0:
        # At most zero true variables: force every x_v to false.
        for v in range(n):
            clauses.append([-x(v)])
        return {"num_vars": n, "clauses": clauses}

    # Sinz sequential counter.
    # s[i][j] (1 <= i <= n, 1 <= j <= k) means "at least j of x_1..x_i true".
    # Auxiliary variables are numbered n+1, n+2, ...
    start = n + 1

    def s(i, j):
        # i in 1..n, j in 1..k
        return start + (i - 1) * k + (j - 1)

    num_vars = n + n * k

    for i in range(1, n + 1):
        xi = x(i - 1)
        # (not x_i or s_{i,1})
        clauses.append([-xi, s(i, 1)])
        if i >= 2:
            # (not s_{i-1,1} or s_{i,1})
            clauses.append([-s(i - 1, 1), s(i, 1)])
            # (not x_i or not s_{i-1,k})  -- would make k+1 true
            clauses.append([-xi, -s(i - 1, k)])
            for j in range(2, k + 1):
                # (not x_i or not s_{i-1,j-1} or s_{i,j})
                clauses.append([-xi, -s(i - 1, j - 1), s(i, j)])
                # (not s_{i-1,j} or s_{i,j})
                clauses.append([-s(i - 1, j), s(i, j)])

    return {"num_vars": num_vars, "clauses": clauses}

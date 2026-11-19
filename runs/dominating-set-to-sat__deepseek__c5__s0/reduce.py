"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (DominatingSet):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (meaning "v is in the
dominating set D").  The formula is satisfiable exactly when some D of size at
most k dominates the graph:

  * Domination: for every vertex u the clause
        (x_u OR x_{v1} OR ... OR x_{vd})
    where v1..vd are the neighbours of u.  This says u is in D or has a
    neighbour in D.  An isolated vertex yields the unit clause (x_u).

  * Cardinality: |D| <= k.  Encoded with Sinz's sequential counter, which
    uses O(n*k) auxiliary variables and clauses (polynomial in the input).
    Special cases:
      - k >= n : every subset has size <= k, so no cardinality clauses are
                 needed (all-true assignment already satisfies domination).
      - k < 0  : impossible, emit the empty clause (unsatisfiable).
      - k == 0 : emit unit clauses (-x_v) for all v.

The construction is polynomial: O(n + m) domination clauses plus O(n*k)
cardinality clauses and variables, with k < n in the only non-trivial branch.
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # x_v is variable number v + 1 (variables are 1-based).
    def x(v: int) -> int:
        return v + 1

    clauses = []

    # --- Domination constraints -------------------------------------------
    neighbours = [[] for _ in range(n)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    for u in range(n):
        clauses.append([x(u)] + [x(v) for v in neighbours[u]])

    num_vars = n

    # --- Cardinality constraint sum x_v <= k ------------------------------
    if k < 0:
        # Unsatisfiable regardless of the graph.
        clauses.append([])
    elif k < n:
        if k == 0:
            for v in range(n):
                clauses.append([-x(v)])
        else:
            # Sinz sequential counter: s(i, j) for i in 1..n, j in 1..k,
            # meaning "among x_1..x_i at least j are true".
            # Variable number of s(i, j):
            def s(i: int, j: int) -> int:
                return n + (i - 1) * k + j

            num_vars = n + n * k

            for i in range(1, n + 1):
                # x_i -> s(i, 1)   (i-th vertex has index i-1)
                clauses.append([-x(i - 1), s(i, 1)])
            for i in range(2, n + 1):
                # s(i-1, 1) -> s(i, 1)
                clauses.append([-s(i - 1, 1), s(i, 1)])
                # x_i and s(i-1, k) cannot both hold
                clauses.append([-x(i - 1), -s(i - 1, k)])
            for i in range(2, n + 1):
                for j in range(2, k + 1):
                    # x_i and s(i-1, j-1) -> s(i, j)
                    clauses.append([-x(i - 1), -s(i - 1, j - 1), s(i, j)])
                    # s(i-1, j) -> s(i, j)
                    clauses.append([-s(i - 1, j), s(i, j)])

    return {"num_vars": num_vars, "clauses": clauses}

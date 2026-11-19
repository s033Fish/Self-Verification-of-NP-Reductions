"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
Sat instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For 1 <= k <= n we use variables x_{i,v} (1-indexed) meaning "vertex v is the
i-th chosen clique vertex", for i in 0..k-1 and v in 0..n-1.

Clauses:
  * for each i: (x_{i,0} or ... or x_{i,n-1})        -- position i is filled
  * for each i, u < v: (not x_{i,u} or not x_{i,v})   -- at most one per position
  * for each v, i < j: (not x_{i,v} or not x_{j,v})   -- each vertex used once
  * for each non-edge {u,v}, i != j:
        (not x_{i,u} or not x_{j,v})                  -- chosen vertices adjacent

A satisfying assignment picks exactly one distinct vertex per position, and the
non-edge clauses force every pair of chosen vertices to be adjacent: a clique of
size k.  Since any subset of a clique is a clique, a clique of size >= k exists
iff one of size exactly k exists.

Edge cases:
  * k <= 0: always yes -> the empty CNF (no clauses), which is satisfiable.
  * k > n:  always no  -> a CNF containing the empty clause, which is never
    satisfiable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0 is always yes: return a trivially satisfiable formula.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n is always no: return a trivially unsatisfiable formula.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n, so n >= 1.
    adjacent = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacent[u][v] = True
        adjacent[v][u] = True

    num_vars = k * n

    def var(i, v):
        """Variable 1..k*n for 'vertex v is the i-th clique vertex'."""
        return i * n + v + 1

    clauses = []

    # Each position i must contain at least one vertex.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Each vertex may be used in at most one position.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # Chosen vertices must be pairwise adjacent: forbid every ordered pair of
    # distinct positions from holding the two ends of a non-edge.
    for u in range(n):
        for v in range(u + 1, n):
            if not adjacent[u][v]:
                for i in range(k):
                    for j in range(k):
                        if i != j:
                            clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

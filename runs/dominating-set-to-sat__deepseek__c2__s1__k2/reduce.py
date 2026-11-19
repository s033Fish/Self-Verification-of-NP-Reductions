"""Polynomial-time reduction from Dominating Set to SAT.

Dominating Set instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:            {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 we introduce a Boolean variable x_v (numbered
v + 1) meaning "v is chosen in the dominating set D".

1. Domination: for every vertex v, the clause

       (x_v OR OR_{u adjacent to v} x_u)

   says that v is either in D or has a neighbour in D.

2. Cardinality: |D| <= k is encoded with the standard sequential-counter
   (Sinz) at-most-k encoding using auxiliary variables s_{i,j}
   (1 <= i <= n, 1 <= j <= k), meaning "at least j of x_1..x_i are true".
   The clauses are:

       (not x_i or s_{i,1})                      1 <= i <= n
       (not s_{i-1,1} or s_{i,1})                2 <= i <= n
       (not x_i or not s_{i-1,j-1} or s_{i,j})   2 <= i <= n, 2 <= j <= k
       (not s_{i-1,j} or s_{i,j})                2 <= i <= n, 2 <= j <= k
       (not x_i or not s_{i-1,k})                2 <= i <= n

   This formula is satisfiable iff at most k of the x_i are true.

Edge cases
----------
* k < 0: the answer is always "no"; return the unsatisfiable formula [[]].
* k >= n (with k >= 0): the answer is always "yes" (including n = 0);
  return the empty formula (no clauses), which is satisfiable.
* Otherwise 0 <= k < n and the construction above applies.  For k = 0 the
  at-most-k constraint simply becomes the unit clauses (not x_v) for all v.

The reduction is polynomial: O(n + |E| + n*k) clauses and n + n*k variables.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always a "no" instance.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n is always a "yes" instance (this also covers n == 0, k >= 0).
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here: 0 <= k < n.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []

    # 1. Domination clauses: x_v = variable v + 1.
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    # 2. At-most-k cardinality constraint.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
    else:
        def s(i, j):
            # Auxiliary variable s_{i,j}, with i in 1..n and j in 1..k.
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
            clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

SOURCE (Dominating Set): {"n": n, "edges": [[u, v], ...], "k": k}
TARGET (SAT):            {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v (0..n-1) introduce a boolean variable x_v (encoded as the
integer v+1) meaning "v is in the dominating set D".

* For every vertex u add the clause
      [x_u] + [x_v for v adjacent to u]
  which says u is dominated (u itself or one of its neighbours is in D).

* Add an "at most k" cardinality constraint over x_0..x_{n-1}.  This is done
  with the standard sequential (Sinz) counter, which uses O(n*k) auxiliary
  variables s(i, j) meaning "at least j of x_0..x_{i-1} are true" and O(n*k)
  clauses.  Since we only reach this branch when 0 <= k < n, this is O(n^2).

Edge cases:
* k < 0  -> no instance; return the unsatisfiable formula with an empty clause.
* k >= n -> yes instance (all n vertices dominate); return the empty formula.
* k = 0  -> force every x_v false with unit clauses; the domination clauses then
            become empty exactly when n > 0 (n = 0 was handled by k >= n).

The formula is satisfiable iff G has a dominating set of size at most k.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always "no".
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n is always "yes" (take all vertices).
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n.
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)

    clauses = []

    # Domination clauses: vertex u must be in D or adjacent to a vertex in D.
    for u in range(n):
        clauses.append([u + 1] + [v + 1 for v in adjacency[u]])

    # At most zero vertices may be selected.
    if k == 0:
        for v in range(1, n + 1):
            clauses.append([-v])
        return {"num_vars": n, "clauses": clauses}

    # Sequential counter for "at most k".
    # s(i, j) is defined for 1 <= i <= n and 1 <= j <= min(i, k).
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # (not x_i) or s(i, 1)
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # (not s(i-1, 1)) or s(i, 1)
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    # (not x_i) or (not s(i-1, j-1)) or s(i, j)
    for i in range(2, n + 1):
        for j in range(2, min(i, k) + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])

    # (not s(i-1, j)) or s(i, j)
    for i in range(2, n + 1):
        for j in range(2, min(i - 1, k) + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # (not x_i) or (not s(i-1, k)): cannot pick a (k+1)-st vertex.
    for i in range(k + 1, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

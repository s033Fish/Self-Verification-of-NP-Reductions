"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v we introduce a Boolean variable x_v (variable number v+1)
meaning "v belongs to the dominating set D".

Domination: for every vertex v the clause

    (x_v  OR  OR_{u adjacent to v} x_u)

expresses that v is in D or has a neighbour in D.

Cardinality: we must also express |D| <= k.  This is encoded with the
sequential counter of Sinz using auxiliary variables s_{i,j} meaning
"among x_1..x_i at least j are true" (i = 1..n, j = 1..k):

    (not x_i or s_{i,1})                          for i = 1..n
    (not s_{i-1,j} or s_{i,j})                    for i = 2..n, j = 1..k
    (not x_i or not s_{i-1,j-1} or s_{i,j})       for i = 2..n, j = 2..k
    (not x_i or not s_{i-1,k})                    for i = 2..n

The last clause forbids a (k+1)-st selected vertex, so the formula is
satisfiable iff the graph has a dominating set of size at most k.

The encoding uses n + n*k variables and O(n*k + |E|) clauses, hence is
polynomial (in fact quadratic) in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build adjacency lists.
    adj = [set() for _ in range(n)]
    for edge in edges:
        u, v = edge[0], edge[1]
        adj[u].add(v)
        adj[v].add(u)

    # k < 0 is always a no-instance: emit an unsatisfiable empty clause.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Domination clauses: vertex v must be in D or adjacent to a member of D.
    clauses = []
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    # k >= n: choosing all vertices always dominates, so no cardinality
    # constraint is needed.  (n == 0 with k >= 0 yields no clauses: yes.)
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # Now 0 <= k < n, so n >= 1.
    # k == 0: no vertex may be selected.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: sequential counter encoding of "at most k true".
    def s(i, j):
        # Auxiliary variable for "at least j of x_1..x_i are true".
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": n + n * k, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v we introduce a variable x_v (variable number v+1, using
1-based SAT variables).  x_v is true iff v is chosen in the dominating set.

Domination: for every vertex u add the clause
    (x_u OR x_{v1} OR ... OR x_{v_d})
where v1..v_d are the neighbours of u.  This forces every vertex to be in D
or adjacent to a vertex of D.

Cardinality "at most k": we use Sinz's sequential counter encoding.
Auxiliary variables s_{i,j} (1 <= i <= n, 1 <= j <= k) mean "among
x_1..x_i at least j are true".  The clauses are:

    (not x_i or s_{i,1})                     for 1 <= i <= n
    (not s_{i-1,1} or s_{i,1})               for 2 <= i <= n
    (not x_i or not s_{i-1,j-1} or s_{i,j})  for 2 <= i <= n, 2 <= j <= k
    (not s_{i-1,j} or s_{i,j})               for 2 <= i <= n, 2 <= j <= k
    (not x_i or not s_{i-1,k})               for 2 <= i <= n

Edge cases are handled directly:
  * k < 0        -> unsatisfiable (single empty clause)
  * k >= n       -> satisfiable (empty formula); n == 0 with k >= 0 too
  * k == 0       -> all x_v must be false, plus domination clauses
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n (including n == 0, k >= 0) is always yes.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Adjacency lists (undirected, no self loops in valid instances).
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses = []

    # Domination clauses.  x_v is variable number v + 1.
    for u in range(n):
        clause = [u + 1]
        for v in adj[u]:
            clause.append(v + 1)
        clauses.append(clause)

    if k == 0:
        # At most 0 chosen vertices: every x_v is false.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s_{i,j} with 1 <= i <= n, 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # (not x_i or s_{i,1})
    for i in range(1, n + 1):
        clauses.append([-(i), s(i, 1)])

    # (not s_{i-1,1} or s_{i,1})
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    # (not x_i or not s_{i-1,j-1} or s_{i,j})
    # (not s_{i-1,j} or s_{i,j})
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])

    # (not x_i or not s_{i-1,k})
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

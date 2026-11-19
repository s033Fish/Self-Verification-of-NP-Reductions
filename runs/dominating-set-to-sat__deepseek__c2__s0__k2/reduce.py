"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (DominatingSet):
    {"n": n, "edges": [[u, v], ...], "k": k}
Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (numbered 1..n), meaning
"v is put into the dominating set D".

Domination: for every vertex v the clause

    (x_v OR x_u1 OR ... OR x_ud)          (u_i the neighbours of v)

forces v to be in D or to have a neighbour in D.

Cardinality "|D| <= k": encoded with Sinz's sequential counter, which uses
O(n*k) auxiliary variables and clauses.  This is polynomial because we only
build it when 0 <= k < n (so k < n).  For k >= n the constraint is vacuous and
is omitted; for k < 0 the instance is a no-instance and we emit an empty clause.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: always a no-instance.  Emit the unsatisfiable formula [[]].
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n = 0: yes for every k >= 0; the empty formula is satisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Build adjacency lists (undirected, no self loops).
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []

    # Domination clauses.  Variable for vertex v is v + 1.
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    # k >= n: "at most k" is vacuous; the domination clauses are satisfiable
    # by taking D = all vertices.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 0 <= k < n from here on.

    # k == 0: D must be empty, i.e. every x_v is false.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: Sinz sequential counter for at-most-k.
    # Auxiliary variable s(i, j) (1 <= i <= n, 1 <= j <= k) means "among the
    # first i vertex variables at least j are true".
    def s(i, j):
        return n + (i - 1) * k + j

    # (not x_i or s(i,1))
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # (not s(i-1,1) or s(i,1))
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    for i in range(2, n + 1):
        for j in range(2, k + 1):
            # (not x_i or not s(i-1,j-1) or s(i,j))
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # (not s(i-1,j) or s(i,j))
            clauses.append([-s(i - 1, j), s(i, j)])

    # (not x_i or not s(i-1,k)): adding x_i would exceed k.
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 we introduce a Boolean variable x_v (encoded as
the integer v+1) meaning "v belongs to the dominating set D".

1. Domination: for every vertex u add the clause

       [x_u] + [x_v for v adjacent to u]

   which says that u is in D or has a neighbour in D.  An isolated vertex
   therefore yields the unit clause [x_u].

2. Cardinality: |D| <= k.  If k >= n this is vacuous.  If k < 0 the instance
   is unsatisfiable, encoded by the empty clause.  Otherwise we use the
   sequential-counter (Sinz) encoding of "at most k of x_1..x_n are true",
   which uses O(n*k) auxiliary variables and clauses:

       s(i, j)  <=>  at least j of x_1..x_i are true     (1 <= i <= n, 1 <= j <= k)

       (not x_i or s(i,1))                          for 1 <= i <= n
       (not s(i-1,j) or s(i,j))                     for 2 <= i <= n, 1 <= j <= k
       (not x_i or not s(i-1,j-1) or s(i,j))        for 2 <= i <= n, 2 <= j <= k
       (not x_i or not s(i-1,k))                    for 2 <= i <= n

The construction is satisfiable exactly when the graph has a dominating set
of size at most k, and its size is polynomial in the input.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no set of at most k vertices exists -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n == 0: the empty set dominates the empty graph; k >= 0 here.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Undirected adjacency sets.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []

    # Domination clauses.  Vertex v is represented by variable v + 1.
    for u in range(n):
        clause = [u + 1]
        for v in adj[u]:
            clause.append(v + 1)
        clauses.append(clause)

    # k >= n: "at most k" is vacuous; all-true satisfies every domination clause.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 0 <= k < n from here on.

    # At most 0: every vertex variable must be false.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s(i, j), 1-indexed, i in 1..n, j in 1..k.
    def s_var(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    for i in range(1, n + 1):
        # x_i -> s(i, 1)
        clauses.append([-i, s_var(i, 1)])

        if i >= 2:
            # s(i-1, j) -> s(i, j)
            for j in range(1, k + 1):
                clauses.append([-s_var(i - 1, j), s_var(i, j)])

            # x_i and s(i-1, j-1) -> s(i, j)
            for j in range(2, k + 1):
                clauses.append([-i, -s_var(i - 1, j - 1), s_var(i, j)])

            # x_i and s(i-1, k) cannot both be true (would give k+1 selected).
            clauses.append([-i, -s_var(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

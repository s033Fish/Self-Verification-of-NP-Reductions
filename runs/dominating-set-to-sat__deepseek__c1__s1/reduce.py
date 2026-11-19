"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (DominatingSet):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (variable number v+1),
meaning "v is placed in the dominating set D".

* Domination: for every vertex u the clause
      (x_u  or  OR_{v adjacent to u} x_v)
  forces u to be dominated (an isolated vertex gives the unit clause (x_u)).

* Cardinality: |D| <= k is encoded with a sequential counter (Sinz
  encoding).  Auxiliary variables s_{i,j} mean "at least j of x_1..x_i are
  true".  The clauses are

      (~x_i or s_{i,1})                       for 1 <= i <= n
      (~s_{i-1,1} or s_{i,1})                 for 2 <= i <= n
      (~x_i or ~s_{i-1,j-1} or s_{i,j})       for 2 <= i <= n, 2 <= j <= k
      (~s_{i-1,j} or s_{i,j})                 for 2 <= i <= n, 2 <= j <= k
      (~x_i or ~s_{i-1,k})                    for 2 <= i <= n

  They are satisfiable exactly when at most k of the x_i are true.  For k = 0
  the unit clauses (~x_i) are used directly.

Edge cases:
    k < 0        -> unsatisfiable formula (empty clause)
    k >= n       -> satisfiable formula (empty formula); this also covers n = 0
    0 <= k < n   -> the construction above
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no dominating set of size at most k exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all vertices is a dominating set of size n <= k.
    # (Also covers n = 0 with k >= 0.)
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n.
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    clauses = []

    # Every vertex must be dominated.
    for u in range(n):
        clauses.append([u + 1] + [v + 1 for v in adjacency[u]])

    if k == 0:
        # No vertex may be selected.
        for i in range(1, n + 1):
            clauses.append([-i])
        num_vars = n
    else:
        def s(i, j):
            """Variable number of the auxiliary s_{i,j}, 1 <= i <= n, 1 <= j <= k."""
            return n + (i - 1) * k + j

        # s_{i,1} holds whenever x_i holds.
        for i in range(1, n + 1):
            clauses.append([-i, s(i, 1)])

        # The counter is monotone in i.
        for i in range(2, n + 1):
            clauses.append([-s(i - 1, 1), s(i, 1)])

        for i in range(2, n + 1):
            for j in range(2, k + 1):
                clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
                clauses.append([-s(i - 1, j), s(i, j)])

        # A (k+1)-st true x is forbidden.
        for i in range(2, n + 1):
            clauses.append([-i, -s(i - 1, k)])

        num_vars = n + n * k

    return {"num_vars": num_vars, "clauses": clauses}

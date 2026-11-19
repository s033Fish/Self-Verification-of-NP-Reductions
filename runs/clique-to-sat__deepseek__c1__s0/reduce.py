"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For a clique of size k we use boolean variables

    x[i][v]  (1-indexed variable i*n + v + 1)

meaning "vertex v is the i-th chosen vertex of the clique",
for i in 0..k-1 and v in 0..n-1.

Clauses:
  * For every position i: (x[i][0] or ... or x[i][n-1])
    (each position must be filled).
  * For every position i and every pair u < v: (~x[i][u] or ~x[i][v])
    (at most one vertex per position).
  * For every pair of positions i < j and every pair (u, v) such that
    u == v or {u, v} is not an edge: (~x[i][u] or ~x[j][v])
    (chosen vertices are pairwise distinct and adjacent).

A satisfying assignment yields k distinct pairwise-adjacent vertices,
i.e. a clique of size k; a clique of size k yields a satisfying
assignment by putting its vertices in the k positions.

Edge cases are handled directly:
  * k <= 0  -> Clique is yes -> return the empty (satisfiable) formula.
  * k >  n  -> Clique is no  -> return a formula with the empty clause.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0 is always yes: an empty CNF is satisfiable.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # A clique can never have more than n vertices.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Build the undirected adjacency set.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    def var(i, v):
        return i * n + v + 1

    num_vars = k * n
    clauses = []

    for i in range(k):
        # At least one vertex in position i.
        clauses.append([var(i, v) for v in range(n)])
        # At most one vertex in position i.
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Cross-position constraints: the i-th and j-th chosen vertices must be
    # distinct and adjacent.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or (u, v) not in adjacent:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

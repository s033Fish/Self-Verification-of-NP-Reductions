"""Polynomial-time reduction from Clique to SAT.

SOURCE (Clique): {"n": n, "edges": [[u, v], ...], "k": k}
  Vertices 0..n-1, undirected simple edges.  Yes iff there is a clique of
  size AT LEAST k.

TARGET (Sat): {"num_vars": m, "clauses": [[literal, ...], ...]}
  Variables 1..m, literals +/-v.  Yes iff some assignment satisfies every
  clause.

Reduction
---------
Edge cases first:
  * k <= 0 : always yes  -> trivially satisfiable formula (no clauses).
  * k >  n : always no   -> formula containing the empty clause [].

Otherwise 1 <= k <= n.  Introduce a boolean variable x(i, v) meaning
"vertex v is the i-th vertex of the clique", for i in 1..k and v in 0..n-1.
Number it var(i, v) = (i - 1) * n + v + 1, so num_vars = k * n.

Clauses:
  1. For every position i: (x(i,0) OR x(i,1) OR ... OR x(i,n-1)).
     Each position picks at least one vertex.
  2. For every position i and every pair u < v:
     (NOT x(i,u) OR NOT x(i,v)).
     Each position picks at most one vertex.
  3. For every pair of positions i < j and every pair of vertices (u, v)
     with u == v or {u, v} not an edge:
     (NOT x(i,u) OR NOT x(j,v)).
     The chosen vertices are distinct and pairwise adjacent.

A satisfying assignment selects exactly one vertex per position; clause 3
makes the k selected vertices distinct and pairwise adjacent, i.e. a clique
of size k.  Conversely any clique of size >= k contains a k-clique, which
yields a satisfying assignment.  Hence the formula is satisfiable iff the
graph has a clique of size >= k.

The construction uses k * n variables and O(k^2 * n^2) clauses, and in the
non-trivial branch k <= n, so it is polynomial in the input size.
"""


def reduce(instance):
    """Return a SAT instance that is yes iff the Clique instance is yes."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- Edge cases -------------------------------------------------------
    if k <= 0:
        # Always a yes-instance: an empty CNF is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always a no-instance: an empty clause can never be satisfied.
        return {"num_vars": 0, "clauses": [[]]}

    # --- Non-trivial case: 1 <= k <= n -----------------------------------
    num_vars = k * n

    def var(i, v):
        # i is 1-based position, v is 0-based vertex.
        return (i - 1) * n + v + 1

    # Adjacency lookup (undirected, no self loops in the input).
    adjacent = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacent[u][v] = True
        adjacent[v][u] = True

    clauses = []

    # 1. At least one vertex per position.
    for i in range(1, k + 1):
        clauses.append([var(i, v) for v in range(n)])

    # 2. At most one vertex per position.
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # 3. Across positions: distinct vertices that are pairwise adjacent.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(n):
                    if u == v or not adjacent[u][v]:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

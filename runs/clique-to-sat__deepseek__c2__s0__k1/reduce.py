"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff the graph on vertices 0..n-1 has a clique of size >= k.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For k >= 1 and k <= n, introduce a boolean variable x_{i,v} for every
position i in 0..k-1 and every vertex v in 0..n-1, meaning "the i-th
vertex of the chosen clique is v".  Variable number is i*n + v + 1, so
num_vars = k*n.

Clauses:
  * For every position i: [x_{i,0}, ..., x_{i,n-1}]  (some vertex is
    chosen at position i).
  * For every position i and every pair u < v: [-x_{i,u}, -x_{i,v}]
    (at most one vertex is chosen at position i).
  * For every pair of positions i < j and every pair of vertices u, v
    that are equal or non-adjacent: [-x_{i,u}, -x_{j,v}] and, when
    u != v, also [-x_{i,v}, -x_{j,u}].  This forbids the same vertex
    appearing twice and forbids two chosen vertices that are not joined
    by an edge.

A satisfying assignment selects exactly one vertex per position, all
distinct (no vertex may appear in two positions), and every pair of
selected vertices is adjacent; hence it is a k-clique.  Conversely any
k-clique yields a satisfying assignment by placing its vertices in the
k positions.  Since the target asks for a clique of size AT LEAST k,
and any clique of size >= k contains a k-subset, this is exact.

Edge cases:
  * k <= 0: always yes -> return the empty (satisfiable) formula.
  * k > n:  always no  -> return a formula containing the empty clause.
  * k = 1:  the construction reduces to "some vertex exists", which is
    satisfiable exactly when n >= 1.

The construction uses O(k*n) variables and O(k^2 * n^2) clauses, so it
runs in polynomial time.
"""


def reduce(instance):
    """Reduce a Clique instance to a SAT instance (both plain dicts)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0 is always a yes-instance: the empty CNF is satisfiable.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n is always a no-instance: the empty clause is unsatisfiable.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Build the adjacency matrix (undirected, no self loops).
    adjacent = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacent[u][v] = True
        adjacent[v][u] = True

    def var(i, v):
        # Position i (0-based) holding vertex v, numbered from 1.
        return i * n + v + 1

    clauses = []

    # At least one vertex per position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Pairwise compatibility between different positions.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or not adjacent[u][v]:
                        clauses.append([-var(i, u), -var(j, v)])
                        if u != v:
                            clauses.append([-var(i, v), -var(j, u)])

    return {"num_vars": k * n, "clauses": clauses}

"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph on vertices 0..n-1 has a clique of size >= k.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
    Yes iff some assignment satisfies every clause.

Reduction
---------
For 1 <= k <= n we introduce one boolean variable x[i][v] for every
group i in 0..k-1 and vertex v in 0..n-1, meaning "the i-th clique
vertex is v".  The clauses are:

  * for every group i:  (x[i][0] or ... or x[i][n-1])       -- group nonempty
  * for every group i and u < v: (-x[i][u] or -x[i][v])     -- group has one vertex
  * for every i < j and every pair (u, v) with u == v or
    {u, v} not an edge: (-x[i][u] or -x[j][v])              -- chosen vertices
                                                               differ and are adjacent

A satisfying assignment selects exactly one vertex per group, and the
cross-group clauses force the k selected vertices to be pairwise distinct
and adjacent, i.e. a k-clique.  Conversely a k-clique yields a satisfying
assignment by putting its vertices into the k groups in any order.

Edge cases:
  * k <= 0: the answer is always yes, so return the empty (satisfiable)
    formula.
  * k > n: the answer is always no, so return a formula containing the
    empty clause (unsatisfiable).

The construction uses k*n variables and O(k^2 * n^2) clauses, so it runs
in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: any graph has a clique of at least k vertices (empty clique).
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: no graph on n vertices can contain a k-clique.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency lookup (both orientations).
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    def var(i, v):
        # Variables are numbered 1..k*n.
        return i * n + v + 1

    clauses = []

    # Each group must contain at least one vertex and at most one vertex.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Vertices chosen by different groups must be distinct and adjacent.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or (u, v) not in adjacent:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": k * n, "clauses": clauses}

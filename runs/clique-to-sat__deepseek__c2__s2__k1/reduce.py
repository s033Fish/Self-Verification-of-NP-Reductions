"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff the graph on vertices 0..n-1 has a clique of at least k vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment to variables 1..m satisfies every clause.

Encoding
--------
For 1 <= k <= n we introduce a boolean variable x_{i,v} for every position
i in 1..k and every vertex v in 0..n-1, meaning "the i-th chosen clique
vertex is v".  The clauses are:

  * for each i:  [x_{i,0}, ..., x_{i,n-1}]           (position i is filled)
  * for each i and u < v:  [-x_{i,u}, -x_{i,v}]      (position i holds one vertex)
  * for each i < j and u:  [-x_{i,u}, -x_{j,u}]      (positions hold distinct vertices)
  * for each i < j, u != v with {u,v} not an edge:
        [-x_{i,u}, -x_{j,v}]                         (chosen vertices are adjacent)

A satisfying assignment picks exactly one distinct vertex per position, and
every pair of chosen vertices is adjacent, i.e. a k-clique.  Conversely a
k-clique yields a satisfying assignment.  Since any clique of size >= k
contains one of size exactly k (for k >= 1), this is equivalent to Clique's
"at least k" condition.

Edge cases:
  * k <= 0 is always yes -> the empty formula (no clauses) is satisfiable.
  * k > n is always no   -> the formula containing the empty clause is not.

The construction uses O(k*n) variables and O(k^2 * n^2) clauses, hence runs
in polynomial time in the input size.
"""


def reduce(instance):
    """Reduce a Clique instance to an equisatisfiable SAT instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Clique is always yes for k <= 0.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # Clique is always no when k exceeds the number of vertices.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n, so n >= 1.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def var(i, v):
        # i in 1..k, v in 0..n-1 -> variable index in 1..n*k.
        return (i - 1) * n + v + 1

    clauses = []

    # Each position is filled with at least one vertex.
    for i in range(1, k + 1):
        clauses.append([var(i, v) for v in range(n)])

    # Each position holds at most one vertex.
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Different positions hold different vertices.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                clauses.append([-var(i, u), -var(j, u)])

    # Chosen vertices in different positions must be adjacent.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(n):
                    if u != v and (u, v) not in edge_set:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": n * k, "clauses": clauses}

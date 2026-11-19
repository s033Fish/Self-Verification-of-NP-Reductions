"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding (for the interesting case 1 <= k <= n):
  Variable x_{i,v} (i in 0..k-1, v in 0..n-1) means "position i of the
  clique is occupied by vertex v".  Numbered as i*n + v + 1.

  Clauses:
    * for every position i: (x_{i,0} or ... or x_{i,n-1})
        -> every position is filled.
    * for every position i and u < v: (-x_{i,u} or -x_{i,v})
        -> each position holds at most one vertex.
    * for every vertex v and i < j: (-x_{i,v} or -x_{j,v})
        -> each vertex is used by at most one position.
    * for every i < j and every non-edge {u,v}: 
          (-x_{i,u} or -x_{j,v}) and (-x_{i,v} or -x_{j,u})
        -> the vertices in different positions must be adjacent.

  A satisfying assignment picks k distinct vertices, one per position, that
  are pairwise adjacent, i.e. a k-clique.  Conversely a k-clique yields a
  satisfying assignment.  Since a clique of size >= k contains a clique of
  size exactly k, this decides "clique of at least k vertices".

Edge cases:
  * k <= 0  -> always yes: the empty formula (no clauses).
  * k >  n  -> always no : a formula containing the empty clause.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0 is always yes.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n is always no (here k >= 1).
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n.
    num_vars = k * n

    def var(i, v):
        """Variable for position i (0-based) holding vertex v (0-based)."""
        return i * n + v + 1

    # Adjacency lookup, treating edges as undirected.
    edge_set = set()
    for e in edges:
        u, v = e[0], e[1]
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # Every position must be occupied by some vertex.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # Every position holds at most one vertex.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Every vertex is used by at most one position.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # Vertices in different positions must be joined by an edge.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(u + 1, n):
                    if (u, v) not in edge_set:
                        clauses.append([-var(i, u), -var(j, v)])
                        clauses.append([-var(i, v), -var(j, u)])

    return {"num_vars": num_vars, "clauses": clauses}

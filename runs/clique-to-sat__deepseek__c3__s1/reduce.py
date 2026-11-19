"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff there is a set of at least k pairwise-adjacent vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment satisfies every clause.

Reduction idea
--------------
For 1 <= k <= n we use the classic "k positions" encoding.  Variable
x_{i,v} (i in 0..k-1, v in 0..n-1) means "vertex v is the i-th vertex of
the clique".  Clauses enforce:

  * for every position i, at least one vertex is chosen;
  * for every position i, at most one vertex is chosen;
  * for distinct positions i != j, the chosen vertices are different;
  * for distinct positions i != j and every non-edge {v, w}, the chosen
    vertices are not (v, w) in either order.

A satisfying assignment therefore selects k distinct, pairwise adjacent
vertices, i.e. a clique of size exactly k.  Conversely any clique of size
>= k contains a clique of size exactly k, so the answers agree.

Edge cases:
  * k <= 0  -> always yes: return an empty (trivially satisfiable) formula.
  * k > n   -> always no : return a formula containing the empty clause.
"""


def _satisfiable_formula():
    return {"num_vars": 0, "clauses": []}


def _unsatisfiable_formula():
    # The empty clause [] can never be satisfied.
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Clique edge cases.
    if k <= 0:
        return _satisfiable_formula()
    if k > n:
        return _unsatisfiable_formula()

    # Variable x_{i,v} has index i*n + v + 1, for i in 0..k-1, v in 0..n-1.
    num_vars = k * n

    def var(i, v):
        return i * n + v + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # At least one vertex per position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # Distinct positions get distinct vertices.
    for i in range(k):
        for j in range(i + 1, k):
            for v in range(n):
                clauses.append([-var(i, v), -var(j, v)])

    # Distinct positions must be joined by an edge (in both orders).
    for i in range(k):
        for j in range(i + 1, k):
            for v in range(n):
                for w in range(n):
                    if v != w and (v, w) not in edge_set:
                        clauses.append([-var(i, v), -var(j, w)])

    return {"num_vars": num_vars, "clauses": clauses}

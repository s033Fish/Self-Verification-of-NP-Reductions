"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction (for 1 <= k <= n):
  Variable x_{i,j} (1-indexed as i*k + j, with i in 0..n-1, j in 1..k)
  means "vertex i is the j-th chosen clique vertex".

  Clauses:
    * For every position j: at least one vertex occupies it.
        (x_{0,j} v x_{1,j} v ... v x_{n-1,j})
    * For every position j and every pair i1 < i2: at most one vertex there.
        (~x_{i1,j} v ~x_{i2,j})
    * For every vertex i and every pair j1 < j2: it occupies at most one
      position (so the k chosen vertices are distinct).
        (~x_{i,j1} v ~x_{i,j2})
    * For every non-edge {a, b} and every ordered pair of distinct positions
      j1 != j2: they cannot both be chosen.
        (~x_{a,j1} v ~x_{b,j2})

  A satisfying assignment selects exactly one distinct vertex per position,
  and the non-edge clauses force every pair of selected vertices to be
  adjacent, i.e. a clique of exactly k vertices.

Edge cases:
  * k <= 0 is always yes  -> return the trivially satisfiable formula.
  * k > n  is always no    -> return a formula with the empty clause.
"""


def _var(i, j, k):
    """1-indexed SAT variable for 'vertex i is in position j'."""
    return i * k + j


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: a clique of at least k vertices always exists.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: impossible.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n.
    num_vars = n * k
    clauses = []

    # At least one vertex per position.
    for j in range(1, k + 1):
        clauses.append([_var(i, j, k) for i in range(n)])

    # At most one vertex per position.
    for j in range(1, k + 1):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                clauses.append([-_var(i1, j, k), -_var(i2, j, k)])

    # Each vertex occupies at most one position.
    for i in range(n):
        for j1 in range(1, k + 1):
            for j2 in range(j1 + 1, k + 1):
                clauses.append([-_var(i, j1, k), -_var(i, j2, k)])

    # Non-adjacent pairs cannot both be selected (in different positions).
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in edge_set:
                continue
            for j1 in range(1, k + 1):
                for j2 in range(1, k + 1):
                    if j1 == j2:
                        continue
                    clauses.append([-_var(a, j1, k), -_var(b, j2, k)])

    return {"num_vars": num_vars, "clauses": clauses}

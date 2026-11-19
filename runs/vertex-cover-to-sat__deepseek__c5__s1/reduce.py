"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance (VertexCover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction
---------
Introduce one boolean variable x_v for every vertex v (literal v+1): x_v is
true iff vertex v is put in the cover.

* For every edge {u, v} add the clause [u+1, v+1]: at least one endpoint is
  chosen.

* Encode the cardinality constraint "at most k of the x_v are true" with the
  sequential-counter (Sinz) encoding.  Auxiliary variables s_{i,j} (1 <= i <= n,
  1 <= j <= k) mean "among the first i vertices at least j are chosen".
  The clauses are:
      ( -x_i  v  s_{i,1} )                       for 1 <= i <= n
      ( -s_{i-1,1} v s_{i,1} )                   for 2 <= i <= n
      ( -x_i v -s_{i-1,j-1} v s_{i,j} )          for 2 <= i <= n, 2 <= j <= k
      ( -s_{i-1,j} v s_{i,j} )                   for 2 <= i <= n, 2 <= j <= k
      ( -x_i v -s_{i-1,k} )                      for 2 <= i <= n
  This is satisfiable (extending any assignment of the x's) exactly when at
  most k of the x_v are true, and it uses O(n*k) variables and clauses.

Edge cases:
    k < 0        -> unsatisfiable formula (single empty clause).
    k == 0       -> force every x_v false with unit clauses; the edge clauses
                    then make it unsat iff the graph has an edge.
    k >= n       -> "at most k" is vacuous, so only the edge clauses are used.

All sizes are polynomial in the input size, and no solver is called.
"""

from __future__ import annotations

from problems import SOURCE, TARGET


def _unsat() -> dict:
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict) -> dict:
    SOURCE.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no cover of negative size exists.
    if k < 0:
        return _unsat()

    # Edge clauses: every edge must have a chosen endpoint.
    clauses = [[u + 1, v + 1] for (u, v) in edges]

    # "At most k" is vacuous when k >= n (all vertices always cover the graph).
    if k >= n:
        result = {"num_vars": n, "clauses": clauses}
        TARGET.validate(result)
        return result

    # k == 0: no vertex may be chosen.
    if k == 0:
        clauses.extend([[-v] for v in range(1, n + 1)])
        result = {"num_vars": n, "clauses": clauses}
        TARGET.validate(result)
        return result

    # 1 <= k < n: sequential counter encoding.
    # Auxiliary variable s_{i,j} has index n + (i-1)*k + j, for 1<=i<=n, 1<=j<=k.
    def s(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        # ( -x_i v s_{i,1} )
        clauses.append([-i, s(i, 1)])
    for i in range(2, n + 1):
        # ( -s_{i-1,1} v s_{i,1} )
        clauses.append([-s(i - 1, 1), s(i, 1)])
        for j in range(2, k + 1):
            # ( -x_i v -s_{i-1,j-1} v s_{i,j} )
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # ( -s_{i-1,j} v s_{i,j} )
            clauses.append([-s(i - 1, j), s(i, j)])
        # ( -x_i v -s_{i-1,k} )
        clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    result = {"num_vars": num_vars, "clauses": clauses}
    TARGET.validate(result)
    return result

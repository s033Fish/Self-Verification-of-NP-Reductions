"""Polynomial-time reduction from Vertex Cover to SAT (CNF satisfiability).

Source instance (VertexCover):
    {"n": n, "edges": [[u, v], ...], "k": k}
Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one Boolean variable x_v for every vertex v (v in 1..n, with
x_v true meaning "v is put in the cover").

* Every edge [u, v] yields the clause (x_u OR x_v): at least one endpoint
  must be selected.

* We additionally need "at most k of the x_v are true".  This cardinality
  constraint is encoded with a sequential counter (Sinz encoding) using
  auxiliary variables s(i, j) meaning "at least j of x_1..x_i are true"
  for 1 <= i <= n and 1 <= j <= k.  The clauses are:

      (not x_i or s(i,1))                          for all i
      (not s(i,j) or s(i,j-1))                     monotonicity
      (not s(i-1,j) or s(i,j))                     carry forward
      (not x_i or not s(i-1,j-1) or s(i,j))        increment
      (not x_i or not s(i-1,k))                    catch the (k+1)-th true

  These force s(i,j) to be true whenever at least j of the first i
  variables are true, so the last family of clauses makes more than k
  true variables impossible; conversely, setting each s(i,j) to its
  intended meaning satisfies every clause when at most k x's are true.

The encoding uses O(n*k) variables and clauses, and in the only
non-trivial case (0 <= k < n) this is O(n^2), hence polynomial.

Edge cases:
    k < 0      -> unsatisfiable formula (single empty clause)
    k >= n     -> trivially satisfiable formula (empty clause set)
    k == 0     -> all x_v forced false via unit clauses
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no cover of negative size can exist -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all n vertices always covers every edge -> satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n, so n >= 1.
    def x(v):
        """SAT variable for vertex v (0-based vertices -> 1-based vars)."""
        return v + 1

    # k == 0: the cover must be empty.  Force every x_v false; the edge
    # clauses then decide the answer.
    if k == 0:
        clauses = [[-x(v)] for v in range(n)]
        for u, v in edges:
            clauses.append([x(u), x(v)])
        return {"num_vars": n, "clauses": clauses}

    # k >= 1.  Auxiliary variable s(i, j), 1 <= i <= n, 1 <= j <= k.
    num_vars = n + n * k

    def s(i, j):
        return n + (i - 1) * k + j

    clauses = []

    # Edge coverage: (x_u OR x_v) for every edge.
    for u, v in edges:
        clauses.append([x(u), x(v)])

    # x_i -> s(i,1)
    for i in range(1, n + 1):
        clauses.append([-x(i - 1), s(i, 1)])

    # s(i,j) -> s(i,j-1)
    for i in range(1, n + 1):
        for j in range(2, k + 1):
            clauses.append([-s(i, j), s(i, j - 1)])

    # s(i-1,j) -> s(i,j)
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # (x_i and s(i-1,j-1)) -> s(i,j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-x(i - 1), -s(i - 1, j - 1), s(i, j)])

    # Catch a (k+1)-th true variable: x_i -> not s(i-1,k)
    for i in range(2, n + 1):
        clauses.append([-x(i - 1), -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

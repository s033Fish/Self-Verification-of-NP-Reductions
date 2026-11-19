"""Polynomial-time reduction from Dominating Set to SAT.

Source (Dominating Set): {"n": n, "edges": [[u, v], ...], "k": k}
Target (SAT):            {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v, meaning "v is chosen
in the dominating set D".

* Domination: for every vertex v add the clause
      (x_v OR x_{u1} OR ... OR x_{ud})
  where u1..ud are the neighbours of v.  This says v is in D or adjacent to
  a vertex of D.

* Size bound |D| <= k: encoded with Sinz's sequential counter.  Auxiliary
  variables s_{i,j} (i = 1..n, j = 1..k) mean "at least j of x_1..x_i are
  true".  The clauses are

      (not x_i or s_{i,1})                        for i = 1..n
      (not s_{i-1,j} or s_{i,j})                  for i = 2..n, j = 1..k
      (not x_i or not s_{i-1,j-1} or s_{i,j})     for i = 2..n, j = 2..k
      (not x_i or not s_{i-1,k})                  for i = 2..n

  These force at most k of the x_v to be true.  The encoding uses O(n*k)
  variables and clauses, which is polynomial.

The formula is satisfiable iff the graph has a dominating set of size <= k.
"""


def reduce(instance):
    """Return a SAT instance that is yes iff the Dominating Set instance is yes."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- Trivial edge cases -------------------------------------------------
    # k < 0: no dominating set of size <= k exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: the whole vertex set is a dominating set of size n <= k.
    # (This also covers n = 0 with k >= 0.)
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n, so n >= 1 and k >= 0.

    # --- Adjacency ----------------------------------------------------------
    neighbours = [set() for _ in range(n)]
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)

    clauses = []

    # --- Domination clauses -------------------------------------------------
    # Variable v+1 represents vertex v.
    for v in range(n):
        clause = [v + 1]
        clause.extend(u + 1 for u in sorted(neighbours[v]))
        clauses.append(clause)

    # --- Cardinality bound |D| <= k ----------------------------------------
    if k == 0:
        # At most zero chosen vertices: force every x_v to be false.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s(i, j) for i in 1..n and j in 1..k.
    # Numbering: n + (i - 1) * k + j, so the largest index is n + n*k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # i = 1: if x_1 is true then at least one of the first one is true.
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    for i in range(2, n + 1):
        # Monotonicity: at least j among the first i-1 implies the same
        # for the first i.
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
        # If x_i is true and there are at least j-1 among the first i-1,
        # then there are at least j among the first i.
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
        # x_i together with k already chosen among the first i-1 would
        # give k+1 chosen vertices: forbidden.
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

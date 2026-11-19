"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Vertices 0..n-1, undirected edges, k any integer.
  Yes iff some vertex cover has at most k vertices.

Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Variables 1..m, clauses are lists of non-zero literals.

Encoding
--------
One boolean variable x_v per vertex v (variable number v + 1), meaning
"vertex v is chosen in the cover".

* For every edge [u, v] we add the clause (x_u OR x_v), forcing at least
  one endpoint to be chosen.

* We additionally constrain the number of chosen vertices to be at most k
  using Sinz's sequential-counter (ladder) encoding.  Auxiliary variables
  s[i][j] (1 <= i <= n, 1 <= j <= k) mean "at least j of x_1..x_i are
  true".  The clauses are:

      (~x_i OR s[i][1])                      for 1 <= i <= n
      (~s[i-1][1] OR s[i][1])                for 2 <= i <= n
      (~x_i OR ~s[i-1][j-1] OR s[i][j])      for 2 <= i <= n, 2 <= j <= k
      (~s[i-1][j] OR s[i][j])                for 2 <= i <= n, 2 <= j <= k
      (~x_i OR ~s[i-1][k])                   for 2 <= i <= n

  Together with the edge clauses this is satisfiable iff the graph has a
  vertex cover of size at most k.

Edge cases:
  * k < 0: always no; return a formula containing the empty clause.
  * k >= n: always yes (all vertices cover every edge); return the empty
    formula (trivially satisfiable).
  * k == 0: the at-most-zero constraint is just the unit clauses (~x_v);
    the ladder encoding is degenerate here, so it is handled directly.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover of negative size exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all n vertices covers every edge, so always yes.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    clauses = []

    # Vertex v is represented by SAT variable v + 1.
    # Each edge needs at least one chosen endpoint.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    if k == 0:
        # At most zero vertices may be chosen.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s(i, j) for 1 <= i <= n and 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # (x_i -> s[i][1])
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    for i in range(2, n + 1):
        # monotonicity for the first counter
        clauses.append([-s(i - 1, 1), s(i, 1)])
        # s[i-1][j] -> s[i][j] and the transition for a new true variable
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
        # cannot have k + 1 chosen vertices
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

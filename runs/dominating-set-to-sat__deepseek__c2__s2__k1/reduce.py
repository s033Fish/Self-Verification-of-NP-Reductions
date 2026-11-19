"""Polynomial-time reduction from Dominating Set to SAT.

Source (Dominating Set)
    {"n": n, "edges": [[u, v], ...], "k": k}
    Vertices 0..n-1, undirected simple edges, k any integer.  Yes iff there
    is a set D with |D| <= k such that every vertex is in D or adjacent to a
    vertex of D.

Target (SAT)
    {"num_vars": m, "clauses": [[literal, ...], ...]}
    Variables 1..m, literals +v / -v.  Yes iff some assignment satisfies
    every clause.

Construction
    * One variable x_v (encoded as v+1) for every vertex v, meaning "v is
      put into the dominating set D".
    * For every vertex v add the clause
          x_v  \/  OR_{u adjacent to v} x_u
      which says v is dominated.
    * Add the cardinality constraint "at most k of x_0..x_{n-1} are true"
      using the sequential (Sinz) counter encoding with auxiliary variables
      s_{i,j} meaning "at least j of x_0..x_{i-1} are true".

    If k < 0 the answer is always no: return the unsatisfiable formula [[]].
    If k >= n the answer is always yes: return the satisfiable formula [].
    Otherwise 0 <= k < n, so the encoding uses O(n*k) <= O(n^2) variables
    and clauses; the reduction is polynomial.
"""


def reduce(instance):
    """Return a SAT instance satisfiable iff the Dominating Set instance is yes."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- Trivial cases -------------------------------------------------
    if k < 0:
        # Dominating Set is always "no"; an empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Dominating Set is always "yes" (including n = 0); no clauses is SAT.
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n, hence n >= 1.
    def x(v):
        """SAT variable for vertex v (0 <= v < n)."""
        return v + 1

    clauses = []

    # --- Domination clauses -------------------------------------------
    neighbours = [[] for _ in range(n)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    for v in range(n):
        clauses.append([x(v)] + [x(u) for u in neighbours[v]])

    # --- At-most-k cardinality constraint -----------------------------
    if k == 0:
        # At most zero chosen vertices: every x_v must be false.
        for v in range(n):
            clauses.append([-x(v)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s_{i,j} for 1 <= i <= n and 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # x_i true implies s_{i,1} true.
    for i in range(1, n + 1):
        clauses.append([-x(i - 1), s(i, 1)])

    # s_{i-1,1} true implies s_{i,1} true.
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    # x_i true together with s_{i-1,j-1} implies s_{i,j};
    # s_{i-1,j} true implies s_{i,j} true.
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-x(i - 1), -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])

    # x_i true together with s_{i-1,k} would mean k+1 true variables.
    for i in range(2, n + 1):
        clauses.append([-x(i - 1), -s(i - 1, k)])

    # s_{1,j} is false for j >= 2 (at most one of the first variable is true).
    for j in range(2, k + 1):
        clauses.append([-s(1, j)])

    return {"num_vars": num_vars, "clauses": clauses}

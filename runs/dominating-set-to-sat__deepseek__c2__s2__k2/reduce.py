"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (DominatingSet):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 we introduce a Boolean variable x_v (variable
number v+1) meaning "v belongs to the dominating set D".

* For every vertex v we add the clause
      (x_v or x_{u1} or ... or x_{ud})
  where u1..ud are the neighbours of v.  This says that v is dominated
  (either v itself or a neighbour is in D).

* We additionally require |D| <= k.  This cardinality constraint is encoded
  with the sequential-counter (Sinz) encoding, which uses O(n*k) auxiliary
  variables and clauses.  Auxiliary variable s_{i,j} means "at least j of
  x_1..x_i are true".

The resulting CNF is satisfiable exactly when the graph has a dominating set
of size at most k.

Edge cases are handled directly:
  * k < 0      -> the answer is no; return an unsatisfiable formula [[]].
  * k >= n     -> the answer is yes; return the empty (satisfiable) formula.
  * k == 0     -> at most zero vertices may be chosen; add unit clauses -x_v.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # --- trivial edge cases -------------------------------------------------
    if k < 0:
        # Always "no": a formula containing the empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Always "yes": choose all vertices (also covers n == 0).
        return {"num_vars": 0, "clauses": []}

    # From here on 0 <= k < n.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            adj[u].add(v)
            adj[v].add(u)

    clauses = []

    # Dominating clauses: x_v or one of its neighbours.
    for v in range(n):
        clause = [v + 1]
        for u in sorted(adj[v]):
            clause.append(u + 1)
        clauses.append(clause)

    # At most k selected vertices.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Sequential counter: s(i, j) == "at least j of x_1..x_i are true",
    # for 1 <= i <= n and 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # (not x_i or s_{i,1})
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # (not s_{i-1,1} or s_{i,1})
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    for i in range(2, n + 1):
        for j in range(2, k + 1):
            # (not x_i or not s_{i-1,j-1} or s_{i,j})
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # (not s_{i-1,j} or s_{i,j})
            clauses.append([-s(i - 1, j), s(i, j)])

    # (not x_i or not s_{i-1,k}): cannot have a (k+1)-th true variable.
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

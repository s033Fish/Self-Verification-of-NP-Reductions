"""Polynomial-time reduction from Vertex Cover to SAT.

Source (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}
Target (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v per vertex (SAT variable v + 1), meaning
"vertex v is in the cover".

* For every edge {u, v} add the clause (x_u OR x_v): the chosen vertices must
  cover every edge.
* Enforce "at most k chosen vertices" with the sequential-counter (Sinz)
  encoding.  Auxiliary variable s[i][j] means "at least j of x_1..x_i are
  true".  The encoding uses O(n * k) variables and clauses, hence polynomial
  time.  It is satisfiable together with a given x-assignment exactly when at
  most k of the x's are true.

The whole formula is satisfiable iff the graph has a vertex cover of size at
most k, so the reduction is correct.

Edge cases
----------
* k < 0: never yes -> return the formula containing the empty clause.
* k >= n: always yes (all vertices cover every edge) -> return an empty,
  satisfiable formula.
* k == 0: the counter encoding degenerates; force every x_v to false with unit
  clauses, then the edge clauses are satisfiable iff there are no edges.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no: the empty clause can never be satisfied.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n is always yes: taking all vertices covers every edge.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Now 0 <= k < n.
    num_vars = n
    clauses = []

    # x_v is SAT variable v + 1.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # At most zero vertices: force every x_v to false.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": num_vars, "clauses": clauses}

    # Auxiliary s[i][j] = "at least j of x_1..x_i are true", 1 <= i <= n,
    # 1 <= j <= min(i, k).  s[0][*] and s[i][j] with j > i are implicitly
    # false and are not created.
    s = [[None] * (k + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            num_vars += 1
            s[i][j] = num_vars

    for i in range(1, n + 1):
        xi = i  # x_{i-1} has SAT variable (i - 1) + 1 = i.

        # x_i -> s[i][1]
        clauses.append([-xi, s[i][1]])

        # s[i-1][1] -> s[i][1]
        if i >= 2:
            clauses.append([-s[i - 1][1], s[i][1]])

        for j in range(2, min(i, k) + 1):
            # (x_i and s[i-1][j-1]) -> s[i][j]
            clauses.append([-xi, -s[i - 1][j - 1], s[i][j]])
            # s[i-1][j] -> s[i][j]  (only when s[i-1][j] exists)
            if j <= i - 1:
                clauses.append([-s[i - 1][j], s[i][j]])

        # Forbid a (k+1)-th true variable: if the first i-1 already contain k
        # true variables, x_i must be false.
        if i >= k + 1:
            clauses.append([-xi, -s[i - 1][k]])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}
Target instance (SAT / CNF):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
Use one boolean variable x_v (encoded as literal v+1) for each vertex v,
meaning "v is chosen in the cover".

  * For every edge [u, v] add the clause (x_u OR x_v), so at least one
    endpoint is chosen.

  * Enforce that at most k of the x_v are true with Sinz's sequential
    counter encoding.  Auxiliary variable s(i, j) means "at least j of
    x_1..x_i are true".  The clauses are:
        (not x_i OR s(i, 1))                       for i = 1..n
        (not s(i-1, j) OR s(i, j))                 for i = 2..n, j = 1..k
        (not x_i OR not s(i-1, j-1) OR s(i, j))    for i = 2..n, j = 2..k
        (not x_i OR not s(i-1, k))                 for i = 2..n
    This uses O(n*k) variables and clauses, hence polynomial time/space.

Edge cases:
  * k < 0            -> always no; emit the unsatisfiable empty clause.
  * k >= n           -> always yes (all vertices cover every edge); emit
                        the trivially satisfiable empty formula.
  * k == 0           -> at most zero chosen; force every x_v false.
  * no edges         -> the edge clauses vanish, and the at-most-k part is
                        satisfiable (choose no vertices) for every k >= 0.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no: a formula containing the empty clause.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n is always yes: the empty formula is satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Now 0 <= k < n.
    if k == 0:
        # At most zero chosen vertices: force every x_v false, and keep
        # the edge clauses (they make it unsat whenever an edge exists).
        clauses = [[-(v + 1)] for v in range(n)]
        for u, v in edges:
            clauses.append([u + 1, v + 1])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: edge clauses plus sequential-counter at-most-k.
    num_vars = n + n * k

    def s(i, j):
        # Auxiliary variable for "at least j of x_1..x_i are true",
        # with i in 1..n and j in 1..k.
        return n + (i - 1) * k + j

    clauses = []

    # Edge coverage: x_u OR x_v.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # x_i -> s(i, 1).
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # s(i-1, j) -> s(i, j).
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # x_i and s(i-1, j-1) -> s(i, j).
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])

    # x_i -> not s(i-1, k)  (prevents a (k+1)-th chosen vertex).
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

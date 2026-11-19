"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:          {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
One boolean variable x_v (SAT variable v + 1) for every vertex v in 0..n-1,
where x_v is true iff v is chosen in the cover.

* For every edge (u, v) add the clause [x_u, x_v]: at least one endpoint is
  in the cover.
* Add a cardinality constraint "at most k of the x_v are true" using the
  sequential-counter (Sinz) encoding, which is polynomial in n and k.
  Auxiliary variables s_{i,j} mean "at least j of x_1..x_i are true".

Special cases:
* k < 0: unsatisfiable formula (a single empty clause).
* k >= n: every vertex set of size <= n covers all edges, so no cardinality
  constraint is needed; the edge clauses alone are the answer.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always "no".
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    clauses = []

    # x_v is SAT variable (v + 1).  Every edge must be covered.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # k >= n: "at most k" is trivially true, so only edge clauses matter.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # Here 0 <= k < n.  Enforce "at most k of x_1..x_n are true".
    if k == 0:
        # At most zero true means every x_v is false.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Sequential-counter encoding.  Auxiliary variable ids start after the
    # n vertex variables.
    s = {}
    next_var = n + 1
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            s[(i, j)] = next_var
            next_var += 1
    num_vars = next_var - 1

    # (not x_i or s_{i,1}) for all i
    for i in range(1, n + 1):
        clauses.append([-i, s[(i, 1)]])

    # (not s_{i-1,1} or s_{i,1}) for i = 2..n
    for i in range(2, n + 1):
        clauses.append([-s[(i - 1, 1)], s[(i, 1)]])

    # (not x_i or not s_{i-1,j-1} or s_{i,j}) for i = 2..n, j = 2..k
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s[(i - 1, j - 1)], s[(i, j)]])

    # (not s_{i-1,j} or s_{i,j}) for i = 2..n, j = 2..k
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-s[(i - 1, j)], s[(i, j)]])

    # (not x_i or not s_{i-1,k}) for i = 2..n: cannot have k+1 true x's
    for i in range(2, n + 1):
        clauses.append([-i, -s[(i - 1, k)]])

    return {"num_vars": num_vars, "clauses": clauses}

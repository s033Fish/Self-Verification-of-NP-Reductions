"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}
Target instance (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 we introduce a Boolean variable x_v (encoded as
the SAT variable v+1) meaning "v is placed in the vertex cover".

* For every edge {u, v} we add the clause (x_u OR x_v), forcing at least one
  endpoint into the cover.
* The requirement that the cover uses AT MOST k vertices is encoded with
  Sinz's sequential-counter at-most-k encoding, using auxiliary variables
  s(i, j) meaning "at least j of x_1..x_i are true".

The encoding is polynomial: O(n*k) auxiliary variables and O(n*k + |E|)
clauses, with k < n in the non-trivial branch.

Edge cases:
    k < 0            -> unsatisfiable (empty clause).
    k >= n           -> always satisfiable (no clauses).
    0 <= k < n       -> sequential-counter encoding (k == 0 handled with units).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover of size at most k exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: all vertices form a cover, so the answer is always yes.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Now 0 <= k < n.
    clauses = []

    # Edge constraints: at least one endpoint in the cover.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # k == 0: no vertex may be selected.
    if k == 0:
        for i in range(1, n + 1):
            clauses.append([-i])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable index for s(i, j), 1 <= i <= n, 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # s(i,1) holds whenever x_i is true.
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    for i in range(2, n + 1):
        # Monotonicity in i for j = 1.
        clauses.append([-s(i - 1, 1), s(i, 1)])
        for j in range(2, k + 1):
            # If x_i is true and there were already j-1 among the first i-1,
            # then there are at least j among the first i.
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # Monotonicity in i for j >= 2.
            clauses.append([-s(i - 1, j), s(i, j)])
        # If x_i is true and the first i-1 already contain k selected
        # vertices, we would exceed k.
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

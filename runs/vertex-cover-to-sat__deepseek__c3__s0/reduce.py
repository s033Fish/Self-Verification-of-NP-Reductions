"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:          {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i (encoded as literal i, i.e. variable i+1)
for every vertex i in 0..n-1.  x_i is true iff vertex i belongs to the cover.

* For every edge {u, v} add the clause [u+1, v+1]: at least one endpoint
  must be selected.
* Enforce "at most k selected vertices" with a sequential counter (Sinz)
  encoding, using auxiliary variables s_{i,j} meaning "at least j of the
  first i vertices are selected".

Edge cases:
* k < 0        -> unsatisfiable (single empty clause).
* k >= n       -> always satisfiable (all vertices cover every edge); the
                  formula has no clauses.
* k == 0       -> force every x_i to false with unit clauses.
* 0 < k < n    -> sequential counter.

The construction uses O(n * k) <= O(n^2) variables and clauses, so it runs
in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover is possible.
    if k < 0:
        return {"num_vars": n, "clauses": [[]]}

    # k >= n: the set of all vertices is a cover of size n <= k.
    if k >= n:
        return {"num_vars": n, "clauses": []}

    clauses = []

    # Edge coverage clauses: for each edge {u, v}, clause (x_u OR x_v).
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    if k == 0:
        # At most zero selected: every vertex variable must be false.
        for i in range(n):
            clauses.append([-(i + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Sequential counter for sum(x_i) <= k, with 0 < k < n.
    # Auxiliary variable s_{i,j} for 1 <= i <= n, 1 <= j <= k.
    # Numbering: aux(i, j) = n + (i - 1) * k + j.
    def s(i, j):
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        # x_i -> s_{i,1}
        clauses.append([-(i), s(i, 1)])

    for i in range(2, n + 1):
        # s_{i-1,1} -> s_{i,1}
        clauses.append([-s(i - 1, 1), s(i, 1)])
        # x_i AND s_{i-1,k} is forbidden (would give k+1 selected).
        clauses.append([-i, -s(i - 1, k)])

    for i in range(2, n + 1):
        for j in range(2, k + 1):
            # x_i AND s_{i-1,j-1} -> s_{i,j}
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # s_{i-1,j} -> s_{i,j}
            clauses.append([-s(i - 1, j), s(i, j)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

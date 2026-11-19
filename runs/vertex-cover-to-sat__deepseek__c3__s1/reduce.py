"""Polynomial-time reduction from Vertex Cover to SAT.

SOURCE: VertexCover
    {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff there is a vertex cover of size at most k.

TARGET: Sat
    {"num_vars": m, "clauses": [[literal, ...], ...]}
    Yes iff the CNF is satisfiable.

Encoding
--------
One boolean variable x_v (v = 1..n) means "vertex v-1 is in the cover".
For every edge {u, v} we add the clause (x_u OR x_v): at least one endpoint
must be selected.

The "at most k selected" constraint is encoded with the sequential counter
(Sinz) encoding, which uses O(n * k) auxiliary variables and clauses and is
therefore polynomial (k < n in the only branch that needs it).

Edge cases:
  * k < 0        -> unsatisfiable formula (empty clause).
  * k >= n       -> trivially satisfiable formula (all vertices cover
                    every edge, so the answer is always yes).
  * k == 0       -> force every x_v false.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no cover of negative size exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: the set of all vertices is a cover of size n <= k.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n.
    edge_clauses = [[u + 1, v + 1] for u, v in edges]

    # k == 0: the cover must be empty, so every vertex is forbidden.
    if k == 0:
        clauses = edge_clauses + [[-(i + 1)] for i in range(n)]
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: variables 1..n are x_1..x_n (vertex 0..n-1).
    # Auxiliary s_{i,j} (1 <= i <= n, 1 <= j <= k) means
    # "at least j of x_1..x_i are true".
    num_vars = n + n * k

    def s(i, j):
        return n + (i - 1) * k + j

    clauses = list(edge_clauses)

    # i = 1
    clauses.append([-1, s(1, 1)])
    for j in range(2, k + 1):
        clauses.append([-s(1, j)])

    # i = 2..n
    for i in range(2, n + 1):
        clauses.append([-i, s(i, 1)])
        clauses.append([-s(i - 1, 1), s(i, 1)])
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
        # More than k true variables are forbidden.
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

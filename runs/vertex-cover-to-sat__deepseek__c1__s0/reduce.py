"""Polynomial-time reduction from Vertex Cover to SAT.

SOURCE (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}
TARGET (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one Boolean variable x_v for every vertex v (meaning "v is in the
cover").  For every edge {u, v} add the clause (x_u OR x_v); these clauses are
satisfied exactly when the set of true x_v's is a vertex cover.

To express "at most k vertices are chosen" we use Sinz's sequential-counter
encoding.  Auxiliary variables s_{i,j} mean "at least j of x_1..x_i are true".
The encoding has O(n * k) variables and clauses.  Because we handle k >= n
separately, in the remaining case 0 <= k < n and therefore n * k < n^2, so the
whole reduction is polynomial in the input size.

Edge cases:
  * k < 0  -> always no; emit the unsatisfiable formula {num_vars: 0, [[]]}.
  * k >= n -> always yes; emit the empty (satisfiable) formula.
  * k == 0 -> at most zero chosen; emit unit clauses (-x_v) plus edge clauses.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover of negative size exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all vertices is a cover, so the answer is always yes.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n.
    if k == 0:
        # At most zero vertices may be chosen: force every x_v false.
        clauses = [[-(v + 1)] for v in range(n)]
        for u, v in edges:
            clauses.append([u + 1, v + 1])
        return {"num_vars": n, "clauses": clauses}

    # Variables: x_i = i for i in 1..n (vertex i-1),
    # auxiliary s_{i,j} = n + (i-1)*k + j for i in 1..n, j in 1..k.
    num_vars = n + n * k

    def s(i, j):
        return n + (i - 1) * k + j

    clauses = []

    # Every edge must be covered.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # Sequential counter for "at most k of x_1..x_n are true".
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
    for i in range(2, n + 1):
        # x_i true while already k chosen among x_1..x_{i-1} is forbidden.
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

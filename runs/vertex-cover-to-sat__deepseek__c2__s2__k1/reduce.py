"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:          {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_v (numbered v + 1) for every vertex v.
  * x_v is true  <=>  vertex v is put into the cover.

For every edge [u, v] add the clause (x_u OR x_v): at least one endpoint
must be chosen.

Finally add a cardinality constraint saying that at most k of the x_v are
true.  This is encoded with the sequential-counter (Sinz) construction,
which uses O(n * k) auxiliary variables and O(n * k) clauses, hence is
polynomial in the input size.

Correctness
-----------
An assignment to the x_v satisfies all edge clauses exactly when the
selected vertices form a vertex cover, and it satisfies the cardinality
constraint exactly when the cover has at most k vertices.  Therefore the
formula is satisfiable iff the graph has a vertex cover of size <= k.

Edge cases
----------
  * k < 0: the source is always "no"; emit the unsatisfiable formula
    containing the empty clause.
  * k >= n: every set of vertices has size <= k, so the cardinality
    constraint is vacuous and is omitted.
  * k == 0: at most zero vertices may be chosen, encoded by unit clauses
    (-x_v) for every vertex.
"""


def reduce(instance):
    """Return a SAT instance equivalent to the Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: Vertex Cover is always "no".  An empty clause is never
    # satisfiable, so the formula is always "no" as well.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    clauses = []

    # One clause per edge: at least one endpoint is in the cover.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # k >= n: "at most k" is vacuous (all n vertices is still <= k).
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # k == 0: no vertex may be chosen.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Here 1 <= k <= n - 1.  Sequential-counter encoding of "at most k
    # of x_1..x_n are true".  Auxiliary variable s(i, j) means "at least j
    # of x_1..x_i are true"; it is numbered n + (i - 1) * k + j.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # x_i -> s(i, 1)
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # s(i - 1, j) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # (x_i and s(i - 1, j - 1)) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])

    # s(i - 1, k) -> not x_i  (a (k+1)-th true variable is forbidden)
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

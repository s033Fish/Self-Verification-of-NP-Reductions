"""Polynomial-time reduction from Vertex Cover to SAT.

Source (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff there is a vertex cover of size at most k.

Target (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}
    Yes iff the CNF is satisfiable.

Construction
------------
Introduce one boolean variable x_v for each vertex v (variable index v + 1);
x_v is true iff v is placed in the cover.

  * For every edge [u, v] add the clause (x_u OR x_v).  This forces the
    chosen vertices to cover every edge.

  * Enforce "at most k of the x_v are true" with the sequential-counter
    (Sinz) encoding.  Auxiliary variable s(i, j) means "at least j of
    x_1..x_i are true" and is numbered n + (i-1)*k + j.  The clauses are

        (~x_i OR s(i,1))                        for 1 <= i <= n
        (~s(i-1,1) OR s(i,1))                   for 2 <= i <= n
        (~x_i OR ~s(i-1,j-1) OR s(i,j))         for 2 <= i <= n, 2 <= j <= k
        (~s(i-1,j) OR s(i,j))                   for 2 <= i <= n, 2 <= j <= k
        (~x_i OR ~s(i-1,k))                     for 2 <= i <= n

    These force s(i,j) true whenever at least j of the first i variables
    are true, and the last clause forbids a (k+1)-th true variable.  The
    encoding is satisfiable iff at most k of the x_v are true.

Special cases:
  * k < 0: always no -> return the unsatisfiable formula with an empty clause.
  * k >= n: the cardinality bound is vacuous, so only the edge clauses are
    needed (always satisfiable, as required since k >= n is always yes).
  * k == 0: force every x_v false with unit clauses (~x_v).

The construction uses O(n*k + |edges|) clauses and O(n*k) variables, so it
runs in polynomial time.  No brute-force solver is used.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: Vertex Cover is always a no-instance.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Clause (x_u OR x_v) for each edge; x_v has index v + 1.
    edge_clauses = [[u + 1, v + 1] for u, v in edges]

    # k >= n: every vertex set of size <= n is allowed, so the bound is
    # vacuous and the edge clauses alone are satisfiable (all true).
    if k >= n:
        return {"num_vars": n, "clauses": edge_clauses}

    # k == 0: at most zero vertices may be chosen.
    if k == 0:
        clauses = list(edge_clauses)
        clauses.extend([[-v] for v in range(1, n + 1)])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: sequential-counter encoding of "at most k".
    def s(i, j):
        # Auxiliary variable "at least j of x_1..x_i are true".
        return n + (i - 1) * k + j

    clauses = list(edge_clauses)
    for i in range(1, n + 1):
        xi = i  # x_i, since x_v = v + 1
        clauses.append([-xi, s(i, 1)])
        if i >= 2:
            clauses.append([-s(i - 1, 1), s(i, 1)])
            for j in range(2, k + 1):
                clauses.append([-xi, -s(i - 1, j - 1), s(i, j)])
                clauses.append([-s(i - 1, j), s(i, j)])
            clauses.append([-xi, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

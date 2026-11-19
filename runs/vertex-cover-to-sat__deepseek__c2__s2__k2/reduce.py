"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:          {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_v for each vertex v (variable v+1), meaning
"v is placed in the cover".

* For every edge {u, v} add the clause (x_u OR x_v): every edge must be
  covered by at least one chosen endpoint.

* Enforce that at most k of the x_v are true, using Sinz's sequential
  counter encoding (a polynomial-size CNF for the cardinality constraint).
  Auxiliary variable s_{i,j} means "at least j of x_1..x_i are true".

The formula is satisfiable iff there is a set of at most k vertices meeting
every edge, i.e. iff the graph has a vertex cover of size <= k.

Special cases
-------------
* k < 0: always no -> emit the unsatisfiable formula containing [].
* k >= n: always yes -> only the edge clauses are needed (all-true works).
* k == 0: no vertex may be chosen -> unit clauses (NOT x_v) plus edge clauses.

The construction uses O(n * k) variables and clauses, hence runs in
polynomial time and never calls any solver.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: Vertex Cover is always a "no" instance.  A formula with an
    # empty clause can never be satisfied, so it is a "no" SAT instance.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Edge clauses: at least one endpoint of every edge must be selected.
    edge_clauses = [[u + 1, v + 1] for (u, v) in edges]

    # k >= n: all vertices form a cover, so the answer is always yes.
    # The edge clauses alone are satisfiable (set every variable true).
    if k >= n:
        return {"num_vars": n, "clauses": edge_clauses}

    # k == 0: no vertex may be selected.  Force every x_v to false; the
    # formula is satisfiable exactly when there are no edges.
    if k == 0:
        clauses = list(edge_clauses)
        clauses.extend([[-v] for v in range(1, n + 1)])
        return {"num_vars": n, "clauses": clauses}

    # General case 1 <= k < n: sequential counter for "at most k true".
    # x_v is variable v+1 (v = 0..n-1).
    # s_{i,j} is variable n + (i-1)*k + j for i in 1..n, j in 1..k.
    def s(i, j):
        return n + (i - 1) * k + j

    clauses = list(edge_clauses)

    # (NOT x_i OR s_{i,1}) for all i
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # (NOT s_{i-1,1} OR s_{i,1}) for i = 2..n
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    # (NOT x_i OR NOT s_{i-1,j-1} OR s_{i,j}) and
    # (NOT s_{i-1,j} OR s_{i,j}) for i = 2..n, j = 2..k
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])

    # (NOT x_i OR NOT s_{i-1,k}) for i = 2..n: a (k+1)-th true is forbidden.
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

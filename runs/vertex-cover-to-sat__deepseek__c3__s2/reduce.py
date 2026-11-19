"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff some set of at most k vertices touches every edge.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
  Yes iff some assignment satisfies every clause.

Reduction
---------
Variable v+1 (for vertex v in 0..n-1) means "vertex v is in the cover".
 * For every edge [u, v] add the clause [u+1, v+1]: at least one endpoint
   must be selected.
 * Add a cardinality constraint "at most k of the n variables are true",
   encoded with Sinz's sequential counter (O(n*k) auxiliary variables and
   clauses), so the whole reduction is polynomial.

Edge cases:
 * k < 0: unsatisfiable, return the empty clause.
 * k >= n: every vertex may be selected, so the edge clauses alone suffice.
 * k == 0: at most 0 true, i.e. every vertex variable is forced false.
"""


def _at_most_k_clauses(n, k, offset):
    """Sinz sequential-counter encoding of sum(x_1..x_n) <= k.

    Variables x_i are numbered offset + i (i = 1..n).  Auxiliary variables
    s_{i,j} ("at least j of x_1..x_i are true", 1 <= j <= k) are numbered
    offset + n + (i - 1) * k + j.  Returns (clauses, num_aux).
    """
    clauses = []
    num_aux = n * k
    s = lambda i, j: offset + n + (i - 1) * k + j

    for i in range(1, n + 1):
        # x_i -> s_{i,1}
        clauses.append([-(offset + i), s(i, 1)])
        if i >= 2:
            # s_{i-1,1} -> s_{i,1}
            clauses.append([-s(i - 1, 1), s(i, 1)])
            # x_i and s_{i-1,k} cannot both hold
            clauses.append([-(offset + i), -s(i - 1, k)])
        for j in range(2, k + 1):
            if i >= 2:
                # x_i and s_{i-1,j-1} -> s_{i,j}
                clauses.append([-(offset + i), -s(i - 1, j - 1), s(i, j)])
                # s_{i-1,j} -> s_{i,j}
                clauses.append([-s(i - 1, j), s(i, j)])
    return clauses, num_aux


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no cover can have negative size -> unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Edge clauses: vertex v is represented by variable v + 1.
    clauses = [[u + 1, v + 1] for u, v in edges]

    # k >= n: selecting all vertices is a valid cover, so the edge clauses
    # alone are satisfiable (assign every variable true).
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 0 <= k < n: add the "at most k" cardinality constraint.
    if k == 0:
        # At most 0 selected: every vertex variable must be false.
        clauses.extend([[-i] for i in range(1, n + 1)])
        return {"num_vars": n, "clauses": clauses}

    extra, num_aux = _at_most_k_clauses(n, k, offset=0)
    clauses.extend(extra)
    return {"num_vars": n + num_aux, "clauses": clauses}

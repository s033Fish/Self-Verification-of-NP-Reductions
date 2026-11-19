"""Polynomial-time reduction from Dominating Set to SAT.

Given a Dominating Set instance {"n": n, "edges": edges, "k": k}, build a
CNF formula that is satisfiable iff the graph has a dominating set of size
at most k.

Encoding
--------
Selection variables x_v (v = 1..n) mean "vertex v-1 is in the set D".

Domination: for every vertex v add the clause

    (x_v OR x_{u1} OR x_{u2} OR ...)

where u1, u2, ... are the neighbours of v.  This says that v is in D or is
adjacent to a vertex of D, so all such clauses together say D dominates.

Cardinality "at most k": Sinz's sequential-counter encoding.  Auxiliary
variables s_{i,j} (1 <= i <= n, 1 <= j <= k) mean "at least j of x_1..x_i
are true".  The clauses are

    (not x_i or s_{i,1})                     for 1 <= i <= n
    (not s_{i-1,1} or s_{i,1})               for 2 <= i <= n
    (not x_i or not s_{i-1,j-1} or s_{i,j})  for 2 <= i <= n, 2 <= j <= k
    (not s_{i-1,j} or s_{i,j})               for 2 <= i <= n, 2 <= j <= k
    (not x_i or not s_{i-1,k})               for 2 <= i <= n

For k = 0 the constraint is just the unit clauses (not x_i).

The counter uses O(n*k) variables and clauses.  Whenever it is built we
have 0 <= k < n, hence n*k < n^2, so the whole reduction is polynomial.

Edge cases are handled directly:
  * k < 0  -> the empty clause, which is unsatisfiable (answer no).
  * k >= n -> no clauses, which is satisfiable (answer yes).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no dominating set exists -> unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: the whole vertex set is a dominating set of size n <= k.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n, so n >= 1.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []

    # Domination clauses: vertex v must be in D or adjacent to D.
    for v in range(n):
        clauses.append([v + 1] + [u + 1 for u in sorted(adj[v])])

    if k == 0:
        # At most zero selected vertices: every x_v is false.
        for v in range(n):
            clauses.append([-(v + 1)])
    else:
        def s(i, j):
            # Auxiliary variable s_{i,j}, i in 1..n, j in 1..k.
            return n + (i - 1) * k + j

        for i in range(1, n + 1):
            clauses.append([-i, s(i, 1)])
        for i in range(2, n + 1):
            clauses.append([-s(i - 1, 1), s(i, 1)])
            for j in range(2, k + 1):
                clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
                clauses.append([-s(i - 1, j), s(i, j)])
            clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

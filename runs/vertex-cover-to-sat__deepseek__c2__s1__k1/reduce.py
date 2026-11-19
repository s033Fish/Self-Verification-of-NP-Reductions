"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
One Boolean variable x_v (encoded as the integer v + 1) per vertex v; x_v
is true exactly when v is chosen in the cover.

* For every edge {u, v} add the clause (x_u OR x_v).  These clauses say
  precisely that the chosen vertices form a vertex cover.

* To express "at most k chosen vertices" we use Sinz's sequential counter
  encoding, which uses O(n * k) auxiliary variables and clauses.  The
  auxiliary variable s_{i,j} (1 <= i <= n-1, 1 <= j <= k) means "at least
  j of x_1..x_i are true".  The clauses are

      (not x_i or s_{i,1})                        1 <= i <= n-1
      (not s_{i-1,1} or s_{i,1})                  2 <= i <= n-1
      (not x_i or not s_{i-1,j-1} or s_{i,j})     2 <= i <= n-1, 2 <= j <= k
      (not s_{i-1,j} or s_{i,j})                  2 <= i <= n-1, 2 <= j <= k
      (not x_i or not s_{i-1,k})                  2 <= i <= n

  The last family forbids a (k+1)-st true x.  If at most k x's are true,
  setting each s_{i,j} to its intended meaning satisfies every clause; if
  more than k are true, the (k+1)-st true x violates the last family.

Edge cases
----------
* k < 0: always a no-instance, so return the unsatisfiable formula [[]].
* k >= n: all n vertices cover every edge, so return the trivially
  satisfiable formula with no clauses.
* k == 0 (and 0 <= 0 < n): the counter encoding degenerates to the unit
  clauses (not x_v) for every vertex, together with the edge clauses.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always a no-instance.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # All n vertices cover every edge, so k >= n is always a yes-instance.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k < n.
    clauses = []

    # Edge clauses: at least one endpoint of every edge must be chosen.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    if k == 0:
        # At most zero vertices may be chosen.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # k >= 1 and n >= 2.  Auxiliary variable s_{i,j} for 1 <= i <= n-1 and
    # 1 <= j <= k is numbered n + (i - 1) * k + j.
    num_vars = n + (n - 1) * k

    def s(i, j):
        return n + (i - 1) * k + j

    # (not x_i or s_{i,1}) for 1 <= i <= n-1.
    for i in range(1, n):
        clauses.append([-i, s(i, 1)])

    # (not s_{i-1,1} or s_{i,1}) for 2 <= i <= n-1.
    for i in range(2, n):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    for i in range(2, n):
        # (not x_i or not s_{i-1,k}).
        clauses.append([-i, -s(i - 1, k)])
        for j in range(2, k + 1):
            # (not x_i or not s_{i-1,j-1} or s_{i,j}).
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            # (not s_{i-1,j} or s_{i,j}).
            clauses.append([-s(i - 1, j), s(i, j)])

    # The final vertex can be the (k+1)-st chosen one.
    clauses.append([-n, -s(n - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

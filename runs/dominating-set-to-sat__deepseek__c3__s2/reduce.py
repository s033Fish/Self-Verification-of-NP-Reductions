"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (SAT / CNF):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one Boolean variable x_v for every vertex v (v = 0..n-1, encoded as
SAT variable v+1), meaning "v belongs to the dominating set D".

* Domination: for every vertex v, the clause
      (x_v OR x_{u1} OR ... OR x_{ud})
  over v and all of its neighbours u1..ud forces every vertex to be dominated.

* Cardinality "at most k": we use Sinz's sequential-counter encoding, which is
  polynomial in n and k.  Auxiliary variables s(i, j) mean "at least j of
  x_1..x_i are true".  The clauses force the s variables to be true whenever
  their meaning holds, and forbid a (k+1)-st true x.

Edge cases are handled directly:
* k < 0            -> unsatisfiable formula (empty clause).
* k >= n           -> always yes; no cardinality constraint is needed.
* k == 0           -> force every x_v false with unit clauses.
* 0 < k < n        -> sequential counter.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: the source is always "no"; return an unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Build the closed neighbourhood N[v] = {v} U {neighbours of v}.
    closed = [set([v]) for v in range(n)]
    for u, v in edges:
        closed[u].add(v)
        closed[v].add(u)

    clauses = []

    # Domination clauses.
    for v in range(n):
        clauses.append([u + 1 for u in sorted(closed[v])])

    # k >= n: any set of at most k vertices is allowed, so the answer is always
    # yes; the domination clauses alone are satisfiable (take all x true).
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 0 <= k < n from here on.

    # k == 0: no vertex may be selected.
    if k == 0:
        for i in range(1, n + 1):
            clauses.append([-i])
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: Sinz sequential counter for "at most k".
    # s(i, j), for 1 <= i <= n-1 and 1 <= j <= k, means "at least j of the
    # first i x-variables are true".
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + (n - 1) * k

    # x_i -> s(i, 1)
    for i in range(1, n):
        clauses.append([-i, s(i, 1)])
    # s(i-1, 1) -> s(i, 1)
    for i in range(2, n):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    # x_i and s(i-1, j-1) -> s(i, j), and s(i-1, j) -> s(i, j)
    for i in range(2, n):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
    # x_i and s(i-1, k) would mean k+1 true values: forbid it.
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

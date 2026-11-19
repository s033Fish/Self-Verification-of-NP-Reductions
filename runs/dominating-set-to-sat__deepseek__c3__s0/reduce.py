"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (variable number v+1),
meaning "v is in the dominating set D".

* Domination: for every vertex u the clause
      (x_u OR x_{w1} OR ... OR x_{wd})
  where w1..wd are the neighbours of u, forces u to be dominated.

* Size bound |D| <= k: a sequential-counter (Sinz) encoding of
  "at most k of x_1..x_n are true" using auxiliary variables s_{i,j}
  ("at least j of x_1..x_i are true").

Edge cases are handled directly:
  k < 0            -> unsatisfiable formula (empty clause)
  n == 0 or k >= n -> satisfiable formula (no clauses)
"""


def _at_most_k_clauses(n, k, offset):
    """CNF clauses over x_1..x_n (variable i) and aux s_{i,j} (offset+...)
    enforcing that at most k of the x variables are true.

    Sequential counter of Sinz (2005).  Returns (clauses, num_aux)."""
    clauses = []
    if k <= 0:
        # at most 0: every x must be false
        for i in range(1, n + 1):
            clauses.append([-i])
        return clauses, 0

    def s(i, j):
        # i in 1..n, j in 1..k
        return offset + (i - 1) * k + j

    # x_i -> s_{i,1}
    for i in range(1, n):
        clauses.append([-i, s(i, 1)])
    # s_{i-1,j} -> s_{i,j}
    for i in range(2, n):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
    # x_i and s_{i-1,j-1} -> s_{i,j}
    for i in range(2, n):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
    # x_i and s_{i-1,k} -> false
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])
    return clauses, n * k


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # n == 0 (yes for k >= 0) and k >= n (take all vertices) are always yes.
    if n == 0 or k >= n:
        return {"num_vars": 0, "clauses": []}

    # Now 0 <= k < n, so n >= 1.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []
    # Domination clauses: variable for vertex v is v + 1.
    for u in range(n):
        clause = [u + 1] + [w + 1 for w in sorted(adj[u])]
        clauses.append(clause)

    # Cardinality bound |D| <= k over variables 1..n.
    card_clauses, num_aux = _at_most_k_clauses(n, k, offset=n)
    clauses.extend(card_clauses)

    return {"num_vars": n + num_aux, "clauses": clauses}

"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (meaning "v is in the
dominating set D").

* Domination: for every vertex v, the clause
      (x_v OR x_{u1} OR ... OR x_{ud})
  where u1..ud are the neighbours of v, forces v to be dominated.

* Cardinality: we must allow at most k chosen vertices.  This is encoded with
  Sinz's sequential counter, using auxiliary variables s_{i,j} meaning
  "among x_1..x_i at least j are true".

Edge cases handled directly:
  * k < 0            -> unsatisfiable formula (empty clause).
  * k >= n           -> the all-true assignment works, so only the domination
                        clauses are needed (always satisfiable).
  * n = 0            -> empty formula, satisfiable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always a NO instance -> return an unsatisfiable CNF.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency lists.
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    def domination_clauses():
        clauses = []
        for v in range(n):
            clause = [v + 1]
            for u in adj[v]:
                clause.append(u + 1)
            clauses.append(clause)
        return clauses

    # k >= n is always a YES instance: take D = all vertices.  Only the
    # domination clauses are needed and they are satisfied by all-true.
    if k >= n:
        return {"num_vars": n, "clauses": domination_clauses()}

    # Now 0 <= k < n.
    clauses = domination_clauses()

    if k == 0:
        # At most zero vertices may be selected.
        for i in range(1, n + 1):
            clauses.append([-i])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variable s(i, j), 1 <= i <= n, 1 <= j <= k.
    def s(i, j):
        return n + (i - 1) * k + j

    num_vars = n + n * k

    # (A) x_i -> s(i, 1)
    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    # (B) s(i-1, j) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # (C) x_i and s(i-1, j-1) -> s(i, j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])

    # (D) x_i -> not s(i-1, k)   (forbids more than k true variables)
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

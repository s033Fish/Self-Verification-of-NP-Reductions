"""Polynomial-time reduction from Dominating Set to SAT.

Source instance (DominatingSet):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (encoded as the SAT
variable v + 1), meaning "v is put into the dominating set".

  * For every vertex v add the clause
        (x_v or x_{u1} or ... or x_{ud})
    over v and all of its neighbours.  Satisfying all these clauses is
    exactly the statement that the chosen set is dominating (an isolated
    vertex yields the unit clause (x_v), forcing v itself into the set).

  * Add a cardinality constraint "at most k of the x_v are true" using the
    polynomial sequential-counter (Sinz) encoding.  Auxiliary variable
    s(i, j) means "at least j of x_1..x_i are true".

The resulting CNF is satisfiable iff the graph has a dominating set of size
at most k.  The construction uses O(n + n*k) variables and O(n*k + |E|)
clauses, hence runs in polynomial time.  No solver is invoked.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # ---- Trivial cases -------------------------------------------------
    if k < 0:
        # Dominating Set is always "no": emit an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Dominating Set is always "yes": emit a satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    # ---- Adjacency lists (0-indexed vertices) --------------------------
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses = []

    # ---- Domination clauses -------------------------------------------
    # Vertex v is SAT variable v + 1.
    for v in range(n):
        clause = [v + 1]
        clause.extend(u + 1 for u in adj[v])
        clauses.append(clause)

    # ---- Cardinality constraint: at most k selected vertices -----------
    # Auxiliary variable s(i, j) is numbered n + (i - 1) * k + j,
    # for i in 1..n and j in 1..k.  x_i is variable i.
    def s(i, j):
        return n + (i - 1) * k + j

    if k == 0:
        # No vertex may be selected.
        for v in range(1, n + 1):
            clauses.append([-v])
    else:
        # x_i -> s(i, 1)
        for i in range(1, n + 1):
            clauses.append([-i, s(i, 1)])
        # s(i-1, j) -> s(i, j)
        for i in range(2, n + 1):
            for j in range(1, k + 1):
                clauses.append([-s(i - 1, j), s(i, j)])
        # x_i and s(i-1, j-1) -> s(i, j)
        for i in range(2, n + 1):
            for j in range(2, k + 1):
                clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
        # x_i -> not s(i-1, k)   (prevents k + 1 selected vertices)
        for i in range(2, n + 1):
            clauses.append([-i, -s(i - 1, k)])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}

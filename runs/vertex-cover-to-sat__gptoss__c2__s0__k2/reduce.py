"""Reduction from Vertex Cover to SAT.

Source problem (VertexCover) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
Target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

We construct a SAT formula that is satisfiable iff the graph has a vertex
cover of size at most k.  The classic reduction uses variables x_{i,j}
meaning "vertex i occupies position j in the cover" for 0 ≤ i < n and
1 ≤ j ≤ k.  The constraints are:
  * Every position j must be occupied by some vertex.
  * No vertex can occupy two different positions (at most one).
  * For each edge (u,v) at least one of its endpoints is selected, i.e.
    the formula contains a clause that is the disjunction of all
    x_{u,·} and x_{v,·}.
These constraints are polynomial in the size of the input.
Edge cases are handled explicitly.
"""

def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases
    if k < 0:
        # Unsatisfiable formula: a single empty clause
        return {"num_vars": 0, "clauses": [[]]}
    if k == 0:
        # Cover of size 0 exists only if there are no edges
        if not edges:
            return {"num_vars": 0, "clauses": []}  # trivially satisfiable
        else:
            return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Always yes – return trivially satisfiable formula
        return {"num_vars": 0, "clauses": []}

    # General case: 0 < k < n
    # Create variables x_{i,j} for vertex i (0..n-1) and position j (0..k-1)
    # Variable numbers start at 1
    def var(i, j):
        return i * k + j + 1

    num_vars = n * k
    clauses = []

    # 1. Every position j must be occupied by at least one vertex
    for j in range(k):
        clause = [var(i, j) for i in range(n)]
        clauses.append(clause)

    # 2. No vertex occupies two different positions (at most one)
    for i in range(n):
        for j1 in range(k):
            for j2 in range(j1 + 1, k):
                clauses.append([-var(i, j1), -var(i, j2)])

    # 3. Edge coverage: for each edge (u,v), at least one endpoint is selected
    for (u, v) in edges:
        clause = []
        for j in range(k):
            clause.append(var(u, j))
            clause.append(var(v, j))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

# The module exposes only the reduce function as required.

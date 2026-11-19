"""Polynomial-time reduction from Hamiltonian Path (undirected) to SAT.

Construction
------------
For a graph with n >= 1 vertices introduce a boolean variable

    x[v, i]   (1 <= var <= n*n)

meaning "vertex v is the i-th vertex of the Hamiltonian path" (0 <= i < n).

The CNF below is satisfiable exactly when the graph has a Hamiltonian path:

  * at least one vertex at every position i:      [x[0,i], ..., x[n-1,i]]
  * every vertex occurs at least once:            [x[v,0], ..., x[v,n-1]]
  * no vertex occurs twice:                       [-x[v,i], -x[v,j]]  for i < j
  * no position holds two vertices:               [-x[u,i], -x[v,i]]  for u < v
  * consecutive positions use graph edges:
        for every ordered pair (u, v) with {u,v} not an edge and every
        i in 0..n-2:                              [-x[u,i], -x[v,i+1]]

The number of variables is n^2 and the number of clauses is O(n^4), so the
reduction runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path; SAT with an empty clause is unsatisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # variable index for "vertex v is at position i"
    def var(v, i):
        return 1 + v * n + i

    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses = []

    # 1. every position is occupied by at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. every vertex appears at least once
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 3. a vertex cannot occupy two positions
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. a position cannot hold two vertices
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 5. consecutive positions must be joined by an edge
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

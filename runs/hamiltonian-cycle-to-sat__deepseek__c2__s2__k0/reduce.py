"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
A Hamiltonian cycle is a cyclic ordering of all n vertices.  We fix vertex 0
at position 0 and use a boolean variable x_{v,i} for every v in 1..n-1 and
every i in 1..n-1, meaning "vertex v sits at position i of the cycle".

The clauses enforce:
  * each position 1..n-1 holds at least one vertex (and at most one),
  * each vertex 1..n-1 appears at least once (and at most once),
  * consecutive positions are joined by an edge,
  * position 1 is adjacent to vertex 0 and position n-1 is adjacent to
    vertex 0 (the two cycle edges incident to vertex 0).

Together these force a bijection between vertices 1..n-1 and positions
1..n-1 whose consecutive pairs (and the pairs with vertex 0 at both ends)
are graph edges, i.e. exactly a Hamiltonian cycle.  The formula is
satisfiable iff such a cycle exists.

Graphs with n <= 2 are always "no"; the reduction returns an unsatisfiable
formula (a single empty clause) for them.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2 can never contain a simple cycle.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}

    # Undirected adjacency matrix.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    # Variable numbering for x_{v,i}, v in 1..n-1, i in 1..n-1.
    var = {}
    idx = 0
    for v in range(1, n):
        for i in range(1, n):
            idx += 1
            var[(v, i)] = idx

    clauses = []

    # Each position has at least one vertex.
    for i in range(1, n):
        clauses.append([var[(v, i)] for v in range(1, n)])

    # Each position has at most one vertex.
    for i in range(1, n):
        for v in range(1, n):
            for w in range(v + 1, n):
                clauses.append([-var[(v, i)], -var[(w, i)]])

    # Each vertex appears at least once.
    for v in range(1, n):
        clauses.append([var[(v, i)] for i in range(1, n)])

    # Each vertex appears at most once.
    for v in range(1, n):
        for i in range(1, n):
            for j in range(i + 1, n):
                clauses.append([-var[(v, i)], -var[(v, j)]])

    # Consecutive positions must be connected by an edge.
    for i in range(1, n - 1):
        for v in range(1, n):
            for w in range(1, n):
                if v != w and not adj[v][w]:
                    clauses.append([-var[(v, i)], -var[(w, i + 1)]])

    # Position 1 must be adjacent to vertex 0 (start of the cycle).
    for v in range(1, n):
        if not adj[v][0]:
            clauses.append([-var[(v, 1)]])

    # Position n-1 must be adjacent to vertex 0 (wrap-around edge).
    for v in range(1, n):
        if not adj[v][0]:
            clauses.append([-var[(v, n - 1)]])

    return {"num_vars": idx, "clauses": clauses}

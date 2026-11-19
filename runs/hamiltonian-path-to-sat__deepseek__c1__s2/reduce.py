"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph on n vertices, introduce a boolean variable x[v][i] for every
vertex v in 0..n-1 and every position i in 0..n-1, meaning "vertex v is the
i-th vertex of the path".

Clauses:
  1. For each position i, at least one vertex occupies it:
         (x[0][i] or x[1][i] or ... or x[n-1][i])
  2. For each vertex v, it occupies at least one position:
         (x[v][0] or x[v][1] or ... or x[v][n-1])
  3. For each position i and each pair u < v, at most one of them is there:
         (-x[u][i] or -x[v][i])
  4. For each vertex v and each pair i < j, it occupies at most one position:
         (-x[v][i] or -x[v][j])
  5. For each consecutive position pair (i, i+1) and each non-edge {u, v}
     with u != v, they cannot be adjacent in the path:
         (-x[u][i] or -x[v][i+1])   and   (-x[v][i] or -x[u][i+1])

Clauses 1-4 force a bijection between vertices and positions; clause 5 then
forces consecutive vertices to be joined by an edge, i.e. a Hamiltonian path.
Conversely any Hamiltonian path gives a satisfying assignment.

Special cases:
  * n = 0: no path exists, so emit the unsatisfiable formula with an empty
    clause.
  * n = 1: the single vertex is a path; clauses 1-2 are satisfiable and no
    adjacency clause exists.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: unsatisfiable (an empty clause can never be satisfied).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Map (vertex, position) -> variable id in 1..n*n.
    def var(v, i):
        return v * n + i + 1

    clauses = []

    # 1. Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Every vertex occupies at least one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 3. At most one vertex per position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 4. At most one position per vertex.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 5. Consecutive path vertices must be joined by an edge.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

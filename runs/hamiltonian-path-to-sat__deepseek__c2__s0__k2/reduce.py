"""Polynomial-time reduction from Hamiltonian Path to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For every vertex v in 0..n-1 and every position i in 0..n-1 we introduce
a Boolean variable x[v][i], meaning "vertex v is the i-th vertex of the
Hamiltonian path".

The clauses enforce:
  1. every position contains at least one vertex;
  2. no position contains two different vertices;
  3. every vertex occurs in at least one position;
  4. no vertex occurs in two different positions;
  5. if u is at position i and v is at position i+1, then {u, v} must
     be an edge of the graph.

Thus a satisfying assignment is exactly a Hamiltonian path, and the
formula is satisfiable iff the graph has one.

The number of variables is n^2 and the number of clauses is O(n^3), so
the reduction runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: the empty graph has no Hamiltonian path.  A formula with an
    # empty clause is unsatisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Variable number for x[v][i], using variables 1..n*n.
    def var(v, i):
        return v * n + i + 1

    clauses = []

    # 1. At least one vertex in each position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. At most one vertex in each position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. At least one position for each vertex.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 4. At most one position for each vertex.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 5. Consecutive positions must be connected by an edge.
    edge_set = {frozenset(edge) for edge in edges}
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph with n vertices introduce a Boolean variable x[v][i] for every
vertex v in 0..n-1 and every position i in 0..n-1, meaning "vertex v is the
i-th vertex of the path".  The variable number is v*n + i + 1.

The clauses are:

1. At least one vertex per position:
       (x[0][i] or x[1][i] or ... or x[n-1][i])          for each i
2. At most one vertex per position:
       (not x[u][i] or not x[v][i])                      for each i, u < v
3. Each vertex at most once:
       (not x[v][i] or not x[v][j])                      for each v, i < j
4. Consecutive positions must be joined by an edge:
       (not x[u][i] or not x[v][i+1])                    for each i < n-1
                                                         and each non-edge {u,v}

Clauses (1) and (2) say every position holds exactly one vertex.  Since there
are n positions and n vertices, clause (3) then forces every vertex to be used
exactly once, so any satisfying assignment is a permutation of the vertices.
Clause (4) makes that permutation a walk in the graph, i.e. a Hamiltonian
path.  Conversely, a Hamiltonian path yields the obvious satisfying assignment.

The formula has n^2 variables and O(n^3) clauses, so the reduction runs in
polynomial time.  The special case n = 0 is unsatisfiable (no Hamiltonian
path); it is encoded with no variables and the empty clause.
"""


def reduce(instance):
    """Reduce a Hamiltonian Path instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: there is no path, so emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = {frozenset(edge) for edge in edges}

    def var(v, i):
        """Variable (1-based) for 'vertex v is at position i'."""
        return v * n + i + 1

    num_vars = n * n
    clauses = []

    # (1) Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # (2) No two different vertices occupy the same position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # (3) No vertex occupies two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # (4) Consecutive positions must be connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": num_vars, "clauses": clauses}

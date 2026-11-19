"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph on n vertices we introduce n*n boolean variables

    x[v][i]  <->  "vertex v is the i-th vertex of the path"

(encoded as the integer  v*n + i + 1).

The CNF uses the following groups of clauses:

1. At least one vertex occupies each position i:
       (x[0][i] or x[1][i] or ... or x[n-1][i])

2. Every vertex occupies at most one position (for v and i < j):
       (not x[v][i] or not x[v][j])

3. Every position holds at most one vertex (for i and u < v):
       (not x[u][i] or not x[v][i])

   Groups 1 and 3 together say that each position holds exactly one
   vertex.  Together with group 2 (each vertex at most once) and the fact
   that there are n positions and n vertices, every vertex is used exactly
   once.

4. For every pair of consecutive positions i, i+1 and every non-edge
   {u, v} of the graph, the two orders are forbidden:
       (not x[u][i] or not x[v][i+1])
       (not x[v][i] or not x[u][i+1])

A satisfying assignment therefore selects a permutation of the vertices
such that every consecutive pair is an edge, i.e. a Hamiltonian path.
Conversely any Hamiltonian path yields a satisfying assignment by setting
x[v][i] true exactly when v is the i-th vertex of the path.

Edge cases
----------
* n = 0: there is no path, so we emit the unsatisfiable formula with no
  variables and a single empty clause.
* n = 1: the single vertex is a path; the formula has one variable and the
  unit clause (x[0][0]).
* n = 2: the adjacency clauses forbid the two non-adjacent orderings
  exactly when the edge {0, 1} is absent.

The formula has n^2 variables and O(n^3) clauses, so the reduction runs in
polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path; the empty clause is never satisfied.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    def var(v, i):
        # Variable for "vertex v is at position i", numbered from 1.
        return v * n + i + 1

    clauses = []

    # 1. At least one vertex at every position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 3. Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(u, i), -var(w, i)])

    # 4. Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for w in range(u + 1, n):
                if (u, w) not in edge_set:
                    clauses.append([-var(u, i), -var(w, i + 1)])
                    clauses.append([-var(w, i), -var(u, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

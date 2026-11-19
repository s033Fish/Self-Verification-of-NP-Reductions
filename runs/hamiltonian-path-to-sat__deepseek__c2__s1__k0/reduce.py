"""Polynomial-time reduction from Hamiltonian Path to SAT.

SOURCE: HamiltonianPath
    {"n": n, "edges": [[u, v], ...]}

TARGET: Sat
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
Introduce a boolean variable x_{i,v} for every position i in 0..n-1 and
every vertex v in 0..n-1, meaning "vertex v is the i-th vertex of the
path".  The variable is numbered  i*n + v + 1  (so variables are
1..n*n).

Clauses:
  * for each position i:  (x_{i,0} v ... v x_{i,n-1})
        -- position i is occupied by some vertex.
  * for each position i and v < w:  (~x_{i,v} v ~x_{i,w})
        -- position i is occupied by at most one vertex.
  * for each vertex v:  (x_{0,v} v ... v x_{n-1,v})
        -- vertex v occurs somewhere.
  * for each vertex v and i < j:  (~x_{i,v} v ~x_{j,v})
        -- vertex v occurs at most once.
  * for each i in 0..n-2 and each ordered pair (u, v) that is not an
    edge of the graph:  (~x_{i,u} v ~x_{i+1,v})
        -- consecutive positions must be joined by an edge.  The case
           u == v is included (a vertex is never adjacent to itself),
           which is consistent with the at-most-once clauses.

A satisfying assignment is exactly a permutation of the vertices in
which every consecutive pair is an edge, i.e. a Hamiltonian path.
Conversely a Hamiltonian path yields a satisfying assignment.

Special case n = 0: no Hamiltonian path exists, so emit the
unsatisfiable formula with one empty clause.

The formula has n*n variables and O(n^3) clauses, so the reduction runs
in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path (and no variables to encode with).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency set (both orientations stored for O(1) lookup).
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    def var(position, vertex):
        """SAT variable for 'vertex occupies position'."""
        return position * n + vertex + 1

    clauses = []

    # Every position holds at least one vertex.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])

    # Every position holds at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # Every vertex occurs at least once.
    for v in range(n):
        clauses.append([var(i, v) for i in range(n)])

    # Every vertex occurs at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if (u, v) not in adjacent:
                    clauses.append([-var(i, u), -var(i + 1, v)])

    return {"num_vars": n * n, "clauses": clauses}

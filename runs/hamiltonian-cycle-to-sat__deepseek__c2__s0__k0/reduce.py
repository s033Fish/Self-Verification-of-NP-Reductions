"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n vertices we introduce n*n boolean variables

    x[v][i]  <->  "vertex v is the i-th vertex of the cycle"

(positions are taken modulo n, so position n-1 is followed by position 0).

The CNF contains the following clauses:

1. Every position holds at least one vertex:
       (x[0][i] or x[1][i] or ... or x[n-1][i])   for each i.
2. Every vertex is used at most once:
       (-x[v][i] or -x[v][j])                     for each v, i < j.
3. Every position holds at most one vertex:
       (-x[u][i] or -x[v][i])                     for each i, u < v.
4. Non-edges cannot be consecutive in the cycle.  For every pair {u,v}
   that is *not* an edge and every position i (with j = (i+1) mod n):
       (-x[u][i] or -x[v][j]) and (-x[v][i] or -x[u][j]).

Clauses 1-3 force the x[v][i] to describe a permutation of the vertices,
i.e. a cyclic ordering, and clauses 4 force every consecutive pair in
that ordering to be an edge.  Hence a satisfying assignment exists iff
the graph has a Hamiltonian cycle.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they are
mapped to the trivially unsatisfiable formula with the empty clause.
"""


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a SAT instance.

    instance: {"n": n, "edges": [[u, v], ...]}
    returns:  {"num_vars": m, "clauses": [[literal, ...], ...]}
    """
    n = instance["n"]

    # A simple graph on fewer than three vertices has no cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Variable number for "vertex v is at position i" (1-based variables).
    def var(v, i):
        return v * n + i + 1

    num_vars = n * n

    # Undirected edge set for fast membership tests.
    edge_set = set()
    for u, v in instance["edges"]:
        edge_set.add((u, v))
        edge_set.add((v, u))

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
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 4. Consecutive positions must be joined by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(u + 1, n):
                if (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])
                    clauses.append([-var(v, i), -var(u, j)])

    return {"num_vars": num_vars, "clauses": clauses}

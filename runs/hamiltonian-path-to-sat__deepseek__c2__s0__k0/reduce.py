"""Polynomial-time reduction from Hamiltonian Path to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}   (undirected, any endpoints)
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
Introduce a Boolean variable x[v][i] for every vertex v in 0..n-1 and every
position i in 0..n-1, meaning "vertex v is the i-th vertex of the path".
Variable number for (v, i) is  v * n + i + 1.

A Hamiltonian path is exactly a permutation of the vertices such that every
pair of consecutive vertices is joined by an edge.  The clauses are:

  * For each position i:  (x[0][i] or x[1][i] or ... or x[n-1][i])
        some vertex occupies position i;
  * For each vertex v:    (x[v][0] or x[v][1] or ... or x[v][n-1])
        vertex v occupies some position;
  * For each position i and u < w:  (~x[u][i] or ~x[w][i])
        at most one vertex per position;
  * For each vertex v and i < j:    (~x[v][i] or ~x[v][j])
        at most one position per vertex;
  * For each i in 0..n-2 and each ordered pair (u, w) with u == w or
    {u, w} not an edge:  (~x[u][i] or ~x[w][i+1])
        consecutive positions must be distinct and joined by an edge.

Together the first four groups force a bijection between vertices and
positions (a permutation), and the last group forces consecutive entries of
that permutation to be adjacent, i.e. a Hamiltonian path.

Edge cases
----------
n == 0: no Hamiltonian path exists; return a formula with the empty clause,
        which is unsatisfiable.
n == 1: the construction yields the single variable x[0][0] with unit clauses,
        which is satisfiable, matching the fact that one vertex is a path.
n == 2: satisfiable iff the edge [0, 1] is present, enforced by the adjacency
        clauses.

The construction uses n^2 variables and O(n^3) clauses, so it runs in
polynomial time.  It never calls the brute-force solvers.
"""


def reduce(instance):
    """Reduce a Hamiltonian Path instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 is always "no": emit an unsatisfiable formula (empty clause).
    if n == 0:
        return {"num_vars": 1, "clauses": [[]]}

    # Undirected adjacency lookup.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    def var(v, i):
        """SAT variable number for 'vertex v is at position i'."""
        return v * n + i + 1

    clauses = []

    # Some vertex at every position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Every vertex at some position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # At most one vertex per position.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(u, i), -var(w, i)])

    # At most one position per vertex.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Consecutive positions must be distinct and connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for w in range(n):
                if u == w or (u, w) not in adjacent:
                    clauses.append([-var(u, i), -var(w, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Variable encoding
-----------------
For a graph on n >= 3 vertices we introduce n*n boolean variables

    x[v][i]  ==  vertex v is the i-th vertex of the Hamiltonian cycle

encoded as the DIMACS variable  v * n + i + 1  (1-based, so all in 1..n*n).

Clauses
-------
1. For every position i, at least one vertex occupies it:
       [x[0][i], x[1][i], ..., x[n-1][i]]
2. For every position i and every pair u < v, at most one of them occupies it:
       [-x[u][i], -x[v][i]]
3. For every vertex v, it occupies at least one position:
       [x[v][0], x[v][1], ..., x[v][n-1]]
4. For every position i (with j = i+1 mod n) and every ordered pair u != v
   such that {u, v} is not an edge, u cannot be at i while v is at j:
       [-x[u][i], -x[v][j]]

Constraints 1 and 2 make each position hold exactly one vertex.  There are n
positions, hence exactly n true x-literals; constraint 3 forces every vertex to
appear, so each vertex appears exactly once.  Constraint 4 forces every pair of
consecutive positions (including the wrap-around pair) to be joined by an edge,
i.e. a Hamiltonian cycle.  Conversely any Hamiltonian cycle satisfies all
clauses, so the reduction is answer-preserving.

Graphs with n <= 2 can never contain a cycle, so they map to the
unsatisfiable formula {"num_vars": 0, "clauses": [[]]}.

The formula has O(n^2) variables and O(n^3) clauses, so the reduction runs in
polynomial time.  No brute-force solver is invoked.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph on fewer than 3 vertices has no cycle: always "no".
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency, stored as ordered pairs for O(1) lookups.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def var(v, i):
        """DIMACS variable for 'vertex v is at position i'."""
        return v * n + i + 1

    clauses = []

    # 1. At least one vertex per position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. At most one vertex per position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. Every vertex appears in at least one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 4. Consecutive positions (cyclically) must be joined by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])

    return {"num_vars": n * n, "clauses": clauses}

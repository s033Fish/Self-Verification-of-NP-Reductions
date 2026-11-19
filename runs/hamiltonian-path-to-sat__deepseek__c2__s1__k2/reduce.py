"""Polynomial-time reduction from Hamiltonian Path to SAT.

SOURCE: Hamiltonian Path (undirected, any endpoints)
    Instance: {"n": n, "edges": [[u, v], ...]}
    Vertices 0..n-1, edges undirected, no self loops / duplicate edges.

TARGET: SAT (CNF satisfiability)
    Instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce a boolean variable x[v][i] (encoded as v*n + i + 1) meaning
"vertex v is the i-th vertex of the Hamiltonian path" for 0 <= v, i < n.

Clauses:

1. Every position is occupied by at least one vertex:
       (x[0][i] v x[1][i] v ... v x[n-1][i])        for each i.

2. Every vertex is used in at most one position:
       (~x[v][i] v ~x[v][j])                        for each v, i < j.

   Together, (1) and (2) force a bijection between vertices and positions:
   there are n positions each needing a vertex and n vertices each usable
   at most once, so every position gets exactly one vertex and every vertex
   is used exactly once.

3. Consecutive positions must be joined by an edge.  For every i < n-1 and
   every ordered pair (u, v), u != v, that is *not* an edge:
       (~x[u][i] v ~x[v][i+1]).

   (The case u == v is already excluded by (2).)

The formula is satisfiable iff the graph has a Hamiltonian path, and it has
O(n^3) variables/clauses, so the reduction is polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path; emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Build an undirected adjacency matrix (edges may be given either way).
    adj = [[False] * n for _ in range(n)]
    for edge in edges:
        u, v = edge[0], edge[1]
        adj[u][v] = True
        adj[v][u] = True

    def var(v, i):
        """Variable saying vertex v is at position i (1-based literals)."""
        return v * n + i + 1

    clauses = []

    # (1) Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # (2) Each vertex is used at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # (3) Consecutive positions must be connected by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and not adj[u][v]:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
Given a graph with n >= 2 vertices, introduce a boolean variable

    x[i][v]  (1-indexed variable number i*n + v + 1)

meaning "vertex v is the i-th vertex of the Hamiltonian path", for
positions i = 0..n-1 and vertices v = 0..n-1.  There are n*n variables.

Clauses:

  1. For every position i, the clause {x[i][0], ..., x[i][n-1]}
     ("some vertex occupies position i").
  2. For every position i and every pair u < v,
     {-x[i][u], -x[i][v]} ("at most one vertex occupies position i").
  3. For every vertex v and every pair i < j,
     {-x[i][v], -x[j][v]} ("vertex v appears at most once").
  4. For every consecutive pair of positions i, i+1 and every ordered
     pair of distinct vertices (u, v) with {u, v} not an edge,
     {-x[i][u], -x[i+1][v]} ("consecutive path vertices must be adjacent").

Clauses 1-3 together force a bijection between positions and vertices
(n positions each holding exactly one vertex, and n vertices each used at
most once).  Clause 4 then forces consecutive vertices to be joined by an
edge, so a satisfying assignment is exactly a Hamiltonian path and vice
versa.

Edge cases:
  * n = 0: no path exists -> return the unsatisfiable formula {[], }.
  * n = 1: the single vertex is a path -> return the empty formula (yes).

The construction uses O(n^2) variables and O(n^3) clauses, so it runs in
polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a Hamiltonian Path instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Edge cases.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        return {"num_vars": 0, "clauses": []}

    def var(i, v):
        # Variable for "vertex v is at position i"; variables are 1..n*n.
        return i * n + v + 1

    # Adjacency set for fast membership tests.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses = []

    # 1. Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])

    # 2. Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # 3. Each vertex is used at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # 4. Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and v not in adj[u]:
                    clauses.append([-var(i, u), -var(i + 1, v)])

    return {"num_vars": n * n, "clauses": clauses}

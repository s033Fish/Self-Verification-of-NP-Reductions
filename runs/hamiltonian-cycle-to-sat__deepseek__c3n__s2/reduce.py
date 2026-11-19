"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

SOURCE = HamiltonianCycle
TARGET = Sat

Encoding
--------
For a graph with n >= 3 vertices we introduce a boolean variable

    x[v][i]   (1-indexed as  v*n + i + 1)

meaning "vertex v is the i-th vertex of the Hamiltonian cycle"
(positions 0..n-1, and position n-1 wraps around to position 0).

Clauses:

  (A) for every position i:      (x[0][i] or x[1][i] or ... or x[n-1][i])
      -> every position is occupied by at least one vertex.

  (B) for every vertex v:        (x[v][0] or x[v][1] or ... or x[v][n-1])
      -> every vertex occupies at least one position.

  (C) for every position i and every pair u < v:
          (~x[u][i] or ~x[v][i])
      -> at most one vertex per position.

  (D) for every vertex v and every pair i < j:
          (~x[v][i] or ~x[v][j])
      -> at most one position per vertex.

  (A)+(C) force exactly one vertex per position, (B)+(D) force exactly one
  position per vertex.  Together they describe a permutation p_0..p_{n-1} of
  the vertices.

  (E) for every position i and every ordered pair (u, v) with u != v such
      that {u, v} is NOT an edge:
          (~x[u][i] or ~x[v][(i+1) mod n])
      -> the vertex after u in the cycle must be adjacent to u.

A satisfying assignment therefore corresponds exactly to a cyclic ordering of
all vertices in which every consecutive pair (including the wrap-around pair)
is an edge, i.e. a Hamiltonian cycle.  Conversely every Hamiltonian cycle
yields a satisfying assignment.

Graphs with n <= 2 have no Hamiltonian cycle (a simple cycle needs at least 3
vertices), so we return the unsatisfiable formula [[1], [-1]] over one
variable.  Note this is also correct for n = 0 and n = 1.

The formula uses n*n variables and O(n^2) clauses, so the reduction runs in
polynomial time.
"""

from __future__ import annotations


def _unsat():
    # A single variable forced both true and false: unsatisfiable.
    return {"num_vars": 1, "clauses": [[1], [-1]]}


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2 can never contain a simple cycle.
    if n <= 2:
        return _unsat()

    # Adjacency set (undirected).
    adj = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    def var(v, i):
        return v * n + i + 1

    clauses = []

    # (A) every position has at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # (B) every vertex occupies at least one position
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # (C) at most one vertex per position
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # (D) at most one position per vertex
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # (E) consecutive vertices in the cycle must be adjacent
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if (u, v) not in adj:
                    clauses.append([-var(u, i), -var(v, nxt)])

    return {"num_vars": n * n, "clauses": clauses}

"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph on n >= 1 vertices we introduce a boolean variable

    x_{i,v}   (1 <= i <= n, 0 <= v < n)

meaning "vertex v occupies position i of the path".

Clauses:
  * For every position i: [x_{i,0}, ..., x_{i,n-1}]
        (each position holds at least one vertex)
  * For every vertex v: [x_{1,v}, ..., x_{n,v}]
        (each vertex appears at least once)
  * For every position i and every pair u < v: [-x_{i,u}, -x_{i,v}]
        (a position holds at most one vertex)
  * For every vertex v and every pair i < j: [-x_{i,v}, -x_{j,v}]
        (a vertex occupies at most one position)
  * For every 1 <= i < n and every ordered pair (u, w), u != w, with
    {u, w} not an edge: [-x_{i,u}, -x_{i+1,w}]
        (consecutive vertices must be joined by an edge)

Together the first four groups force the x variables to describe a
permutation of the vertices; the last group forces consecutive vertices
to be adjacent.  Hence a satisfying assignment exists iff the graph has a
Hamiltonian path.

The special case n = 0 has no Hamiltonian path, so we emit the
unsatisfiable formula containing the empty clause.

The number of variables is n^2 and the number of clauses is O(n^3), so
the reduction runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no Hamiltonian path.  Emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    def var(i: int, v: int) -> int:
        """Variable for 'vertex v is at position i' (0-based i, v)."""
        return i * n + v + 1

    clauses: list[list[int]] = []

    # Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])

    # Each vertex appears at least once.
    for v in range(n):
        clauses.append([var(i, v) for i in range(n)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, w)])

    # Each vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # Consecutive positions must be joined by an edge.
    adjacency = set()
    for u, w in edges:
        adjacency.add((u, w))
        adjacency.add((w, u))
    for i in range(n - 1):
        for u in range(n):
            for w in range(n):
                if u != w and (u, w) not in adjacency:
                    clauses.append([-var(i, u), -var(i + 1, w)])

    return {"num_vars": n * n, "clauses": clauses}

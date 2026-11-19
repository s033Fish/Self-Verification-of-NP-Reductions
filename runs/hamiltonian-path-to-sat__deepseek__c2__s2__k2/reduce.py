"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding
--------
For a graph on n vertices we introduce a Boolean variable x[v][i] for every
pair (v, i) with 0 <= v, i < n, meaning "vertex v is the i-th vertex of the
Hamiltonian path".

  var(v, i) = v * n + i + 1          (variables are 1..n*n)

The CNF contains:

  * for every position i, a clause [x[0][i], ..., x[n-1][i]] saying that some
    vertex occupies position i (at least one);
  * for every vertex v and positions i < j, the clause [-x[v][i], -x[v][j]]
    saying v occupies at most one position;
  * for every position i and vertices u < v, the clause [-x[u][i], -x[v][i]]
    saying position i is occupied by at most one vertex;
  * for every i in 0..n-2 and every ordered pair u != v that is *not* an edge,
    the clause [-x[u][i], -x[v][i+1]] saying u and v cannot be consecutive.

Exactly n positions each holding exactly one vertex, with every vertex used at
most once, forces a permutation of the vertices; the last family of clauses
forces consecutive vertices to be joined by an edge.  Hence the formula is
satisfiable iff the graph has a Hamiltonian path.

Edge cases
----------
n = 0: Hamiltonian Path is "no", so we emit the formula with the empty clause
       [], which is unsatisfiable.
n = 1: one variable x[0][0] and the unit clause [x[0][0]]; satisfiable.
n = 2: satisfiable exactly when the edge [0, 1] is present.

The construction uses O(n^2) variables and O(n^2) clauses, so it runs in
polynomial time and never calls a brute-force solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a Hamiltonian Path instance to a SAT instance (CNF)."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0 has no Hamiltonian path; the empty clause is never satisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency set of frozensets.
    edge_set = {frozenset(edge) for edge in edges}

    def var(v: int, i: int) -> int:
        """Variable saying vertex v is at position i (1-indexed)."""
        return v * n + i + 1

    clauses: list[list[int]] = []

    # Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Every vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Every position is occupied by at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

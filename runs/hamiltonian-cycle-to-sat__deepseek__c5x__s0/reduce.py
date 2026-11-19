"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce n*n boolean variables

    x[v][i]  meaning "vertex v is the i-th vertex of the cycle"

(positions 0..n-1 around the cycle).  The CNF contains:

  * for every vertex v:  (x[v][0] or ... or x[v][n-1])
    and pairwise (not x[v][i] or not x[v][j]) for i < j
      -> every vertex occupies exactly one position;
  * for every position i: (x[0][i] or ... or x[n-1][i])
    and pairwise (not x[u][i] or not x[w][i]) for u < w
      -> every position holds exactly one vertex;
  * for every position i (with j = (i+1) mod n) and every non-edge
    {u, w}: (not x[u][i] or not x[w][j]) and (not x[w][i] or not x[u][j])
      -> consecutive positions must be joined by an edge.

A satisfying assignment is exactly a cyclic ordering of all vertices along
edges of the graph, i.e. a Hamiltonian cycle.  The encoding uses O(n^2)
variables and O(n^3) clauses, so the reduction is polynomial time.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they map to the
trivially unsatisfiable formula containing the empty clause.
"""

from __future__ import annotations

from typing import Any


def _unsat() -> dict[str, Any]:
    """A formula that is never satisfiable (contains the empty clause)."""
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph needs at least 3 vertices to contain a cycle.
    if n <= 2:
        return _unsat()

    edge_set: set[tuple[int, int]] = set()
    for u, v in edges:
        edge_set.add((u, v) if u < v else (v, u))

    def var(v: int, i: int) -> int:
        # variables are 1..n*n
        return v * n + i + 1

    num_vars = n * n
    clauses: list[list[int]] = []

    # Every vertex is placed in exactly one position.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Every position contains exactly one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(u, i), -var(w, i)])

    # Consecutive positions must be connected by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for w in range(u + 1, n):
                if (u, w) not in edge_set:
                    clauses.append([-var(u, i), -var(w, j)])
                    clauses.append([-var(w, i), -var(u, j)])

    return {"num_vars": num_vars, "clauses": clauses}

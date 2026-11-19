"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce a Boolean variable

    x[v][i]   meaning "vertex v occupies position i of the cycle"

for every v in 0..n-1 and i in 0..n-1.  A Hamiltonian cycle is exactly a
cyclic ordering of all vertices in which consecutive vertices (including the
last and the first) are joined by an edge, so we assert:

  * each position holds at least one vertex,
  * each vertex occupies at least one position,
  * each position holds at most one vertex,
  * each vertex occupies at most one position,
  * for every position i, the vertices at positions i and (i+1) mod n are
    adjacent in the graph.

The first four families make the assignment a bijection between vertices and
positions; the last makes the resulting cyclic order a Hamiltonian cycle.
The unit clause x[0][0] is a sound symmetry break: any cycle can be rotated so
that vertex 0 sits at position 0.

Graphs with n <= 2 have no Hamiltonian cycle, so we return the formula with a
single empty clause, which is unsatisfiable for any variable count.

The encoding uses n^2 variables and O(n^3) clauses, so the reduction runs in
polynomial time.  It never calls a solver.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def _unsat() -> Instance:
    """A CNF that is unsatisfiable regardless of the variable count."""
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance: Instance) -> Instance:
    """Reduce a Hamiltonian Cycle instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph needs at least three vertices to contain a cycle.
    if n < 3:
        return _unsat()

    # x(v, i) is variable 1 + v * n + i, for v, i in 0..n-1.
    def x(v: int, i: int) -> int:
        return 1 + v * n + i

    num_vars = n * n
    clauses: list[list[int]] = []

    # Symmetry break: vertex 0 is at position 0.
    clauses.append([x(0, 0)])

    # Every position holds at least one vertex.
    for i in range(n):
        clauses.append([x(v, i) for v in range(n)])

    # Every vertex occupies at least one position.
    for v in range(n):
        clauses.append([x(v, i) for i in range(n)])

    # Every position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-x(u, i), -x(v, i)])

    # Every vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-x(v, i), -x(v, j)])

    # Consecutive positions must be joined by an edge.
    adjacent = {frozenset((u, v)) for u, v in edges}
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(u + 1, n):
                if frozenset((u, v)) not in adjacent:
                    # Forbid u at i with v at j, and the reverse orientation.
                    clauses.append([-x(u, i), -x(v, j)])
                    clauses.append([-x(v, i), -x(u, j)])

    return {"num_vars": num_vars, "clauses": clauses}

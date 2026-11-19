"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

Encoding (position / permutation encoding)
------------------------------------------
For a graph with n >= 3 vertices introduce a boolean variable

    pos(v, k)   meaning "vertex v is the k-th vertex of the cycle"

for every v in 0..n-1 and k in 0..n-1.  Variables are numbered
1..n*n, with pos(v, k) -> v*n + k + 1.

The formula asserts:

  * every vertex occupies exactly one position,
  * every position is occupied by exactly one vertex,
  * the vertices in consecutive positions (cyclically, so position
    n-1 is followed by position 0) are joined by an edge.

Any satisfying assignment is therefore a permutation of the vertices
arranged in a cyclic order in which consecutive vertices are adjacent,
i.e. exactly a Hamiltonian cycle.  Conversely a Hamiltonian cycle gives
a satisfying assignment by listing its vertices in order.

For n <= 2 no simple graph has a cycle, so the reduction emits the
unsatisfiable formula containing the empty clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: a simple graph cannot contain a cycle.
    if n < 3:
        return {"num_vars": 0, "clauses": [[]]}

    adjacent = {frozenset((u, v)) for u, v in edges}

    def var(v: int, k: int) -> int:
        return v * n + k + 1

    num_vars = n * n
    clauses: list[list[int]] = []

    # Every vertex occupies exactly one position.
    for v in range(n):
        clauses.append([var(v, k) for k in range(n)])
        for k in range(n):
            for k2 in range(k + 1, n):
                clauses.append([-var(v, k), -var(v, k2)])

    # Every position is occupied by exactly one vertex.
    for k in range(n):
        clauses.append([var(v, k) for v in range(n)])
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, k), -var(v, k)])

    # Consecutive positions (cyclically) must be joined by an edge.
    for k in range(n):
        nxt = (k + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in adjacent:
                    clauses.append([-var(u, k), -var(v, nxt)])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:           {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_v for every vertex v (variable v+1).
For every edge {u, v} add the clause (x_u OR x_v): this forces the chosen
vertices to form a vertex cover.

The "at most k chosen vertices" side is encoded with the sequential counter
encoding of Sinz (2005), which uses O(n*k) auxiliary variables and clauses,
hence is polynomial in the instance size.

Special cases:
  * k < 0  -> unsatisfiable formula (a single empty clause).
  * k >= n -> trivially satisfiable formula (no clauses); all vertices cover.
  * k == 0 -> only unit clauses (-x_v) plus the edge clauses.
"""

from __future__ import annotations

from typing import Any


def _edge_clauses(n: int, edges: list[list[int]]) -> list[list[int]]:
    """Clause (x_u OR x_v) for each edge, variables numbered v+1."""
    return [[u + 1, v + 1] for u, v in edges]


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover possible -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: all vertices form a cover -> trivially satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Now 0 <= k < n.
    edge_clauses = _edge_clauses(n, edges)

    if k == 0:
        # At most zero vertices may be chosen: every x_v must be false.
        clauses = edge_clauses + [[-(v + 1)] for v in range(n)]
        return {"num_vars": n, "clauses": clauses}

    # Sequential counter variables s_{i,j} (1 <= i <= n, 1 <= j <= k) meaning
    # "at least j of x_1..x_i are true".
    # Variable index of s_{i,j}:
    def s(i: int, j: int) -> int:
        return n + (i - 1) * k + (j - 1) + 1

    num_vars = n + n * k
    clauses: list[list[int]] = list(edge_clauses)

    for i in range(1, n + 1):
        xi = i  # variable for vertex i-1 is i
        # x_i -> s_{i,1}
        clauses.append([-xi, s(i, 1)])

    for i in range(2, n + 1):
        xi = i
        # s_{i-1,1} -> s_{i,1}
        clauses.append([-s(i - 1, 1), s(i, 1)])
        # x_i and s_{i-1,j-1} -> s_{i,j}
        # s_{i-1,j} -> s_{i,j}
        for j in range(2, k + 1):
            clauses.append([-xi, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
        # x_i and s_{i-1,k} cannot both hold (would give k+1 chosen).
        clauses.append([-xi, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

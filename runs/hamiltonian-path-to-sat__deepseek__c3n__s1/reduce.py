"""Polynomial-time reduction from Hamiltonian Path to SAT.

Encoding (standard positional / time-step encoding):

For an input graph with n vertices we introduce n*n boolean variables
    x[v][i]  meaning "vertex v is the i-th vertex of the Hamiltonian path"
represented by the integer literal  v*n + i + 1  (variables are 1..n*n).

Clauses:
  * For every position i: at least one vertex occupies it.
        (x[0,i] or x[1,i] or ... or x[n-1,i])
  * For every vertex v: v occurs at least once.
        (x[v,0] or ... or x[v,n-1])
  * For every vertex v and positions i < j: v cannot be in two positions.
        (~x[v,i] or ~x[v,j])
  * For every position i and vertices u < w: two vertices cannot share it.
        (~x[u,i] or ~x[w,i])
  * For every consecutive pair of positions i, i+1 and every ordered pair of
    distinct vertices (u, w) that is NOT an edge: they cannot be adjacent in
    the path.
        (~x[u,i] or ~x[w,i+1])

Together the first four clause families force the variables to encode a
permutation of the vertices (a linear ordering), and the last family forces
consecutive vertices in that ordering to be joined by an edge.  Hence the
formula is satisfiable iff the graph has a Hamiltonian path.

Edge case n = 0: there is no Hamiltonian path, so we return the formula
{"num_vars": 0, "clauses": [[]]} containing the empty clause, which is
unsatisfiable.

The reduction uses O(n^2) variables and O(n^3) clauses, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: no path exists.  Emit an unsatisfiable formula (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = {frozenset(edge) for edge in edges}

    def var(vertex: int, position: int) -> int:
        return vertex * n + position + 1

    clauses: list[list[int]] = []

    # Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # Each vertex appears at least once.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for w in range(u + 1, n):
                clauses.append([-var(u, i), -var(w, i)])

    # Consecutive vertices must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for w in range(n):
                if u == w:
                    continue
                if frozenset((u, w)) not in edge_set:
                    clauses.append([-var(u, i), -var(w, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}

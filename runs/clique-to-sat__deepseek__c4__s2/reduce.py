"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Yes-condition for Clique: graph has a clique of AT LEAST k vertices.

Reduction
---------
Handle the trivial cases first:
  * k <= 0  -> always yes.  Return a formula with no clauses (satisfiable).
  * k >  n  -> always no.   Return a formula with one empty clause (unsat).

Otherwise 1 <= k <= n.  Introduce boolean variables

    x[i][v]   (0 <= i < k, 0 <= v < n)   meaning "the i-th chosen vertex is v"

encoded as variable number  i * n + v + 1  (so num_vars = k * n).

Clauses:
  (A) for every i:            [x[i][0], ..., x[i][n-1]]        (pick at least one)
  (B) for every i, u < v:     [-x[i][u], -x[i][v]]             (pick at most one)
  (C) for every i < j and every ordered pair (u, v) with
      u == v or {u, v} not an edge:  [-x[i][u], -x[j][v]]
      (the vertices chosen for different positions must be equal or adjacent;
       with (B) they cannot be equal, so distinct positions must be adjacent)

A satisfying assignment picks exactly one vertex per position i, and any two
chosen vertices are adjacent, i.e. a k-clique.  Conversely a clique of size at
least k yields a satisfying assignment by choosing any k of its vertices.
The formula has O(k*n + k^2*n^2) clauses and k*n variables, polynomial in the
input size.
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """Variable number for 'position i holds vertex v' (1-indexed)."""
    return i * n + v + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Trivial cases.
    if k <= 0:
        # Always yes: empty formula is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no: an empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # 1 <= k <= n.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    num_vars = k * n
    clauses: list[list[int]] = []

    # (A) each position picks at least one vertex
    for i in range(k):
        clauses.append([_var(i, v, n) for v in range(n)])

    # (B) each position picks at most one vertex
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # (C) different positions must hold equal or adjacent vertices
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                # same vertex in both positions is forbidden
                clauses.append([-_var(i, u, n), -_var(j, u, n)])
                for v in range(n):
                    if u != v and (u, v) not in edge_set:
                        clauses.append([-_var(i, u, n), -_var(j, v, n)])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
  Yes iff there is a set of at least k pairwise-adjacent vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce a boolean variable x[i][v] for every position i in 1..k and every
vertex v in 0..n-1, meaning "vertex v is the i-th member of the clique".
Variable numbering: var(i, v) = (i - 1) * n + (v + 1), so variables are
1..k*n.

Clauses:
  1. For each position i:  (x[i][0] v x[i][1] v ... v x[i][n-1])
     -> every position is filled.
  2. For each position i and each pair u < v:
        (~x[i][u] v ~x[i][v])
     -> at most one vertex per position.
  3. For each pair of positions i < j and each ordered pair of vertices
     (u, v) with u == v or {u, v} not an edge:
        (~x[i][u] v ~x[j][v])
     -> two positions never pick the same vertex or a non-adjacent pair.
     (u == v is covered because a self-pair is not an edge.)

A satisfying assignment picks, for every position, exactly one vertex, and
all chosen vertices are pairwise distinct and adjacent: a k-clique.  A
k-clique yields a satisfying assignment by putting its vertices into the k
positions.  Hence the formula is satisfiable iff the graph has a clique of
at least k vertices (a clique of size >= k contains one of size exactly k).

Edge cases are handled directly to keep the output small:
  * k <= 0  -> yes  -> empty formula (satisfiable).
  * k >  n  -> no   -> formula with the empty clause (unsatisfiable).
"""

from __future__ import annotations

from typing import Any


def _var(i: int, v: int, n: int) -> int:
    """1-based variable index for 'position i (1-based) holds vertex v'."""
    return (i - 1) * n + (v + 1)


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Trivial cases.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Adjacency set (undirected).
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    num_vars = k * n
    clauses: list[list[int]] = []

    # 1. Each position holds at least one vertex.
    for i in range(1, k + 1):
        clauses.append([_var(i, v, n) for v in range(n)])

    # 2. Each position holds at most one vertex.
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # 3. Different positions hold distinct, adjacent vertices.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(n):
                    if u == v or (u, v) not in adjacent:
                        clauses.append([-_var(i, u, n), -_var(j, v, n)])

    return {"num_vars": num_vars, "clauses": clauses}

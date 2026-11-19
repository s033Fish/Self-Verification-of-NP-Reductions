"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For a non-trivial instance (1 <= k <= n) introduce k*n boolean variables

    x[i][v]   (i = 0..k-1, v = 0..n-1),   variable number i*n + v + 1

with the intended meaning "vertex v is chosen as the i-th vertex of the
clique".  The CNF contains the following clauses:

1. For every position i:
       [x[i][0], x[i][1], ..., x[i][n-1]]
   (some vertex is chosen at position i).

2. For every position i and every pair u < v:
       [-x[i][u], -x[i][v]]
   (at most one vertex is chosen at position i).

3. For every pair of positions i < j and every ordered pair (u, v) of
   vertices that are NOT joined by an edge (this includes u == v, since
   the graph has no self-loops):
       [-x[i][u], -x[j][v]]
   (the vertices chosen at two different positions must be adjacent, and
   in particular must be distinct).

A satisfying assignment selects, for each position, exactly one vertex
(clauses 1 and 2).  Clauses 3 force every pair of selected vertices to be
adjacent, so the selected vertices form a clique of size k.  Conversely a
k-clique yields a satisfying assignment by choosing its vertices in any
order.  Hence the formula is satisfiable iff the graph has a clique of
size at least k.

Edge cases
----------
* k <= 0: Clique is always yes; return the empty CNF (satisfiable).
* k > n:  Clique is always no; return a CNF with the empty clause (unsat).
* k == 1: the formula is satisfiable iff n >= 1, matching Clique.

The construction uses O(k^2 * n^2) clauses and variables, so it runs in
polynomial time in the size of the input instance.
"""

from __future__ import annotations


def _variable(i: int, v: int, n: int) -> int:
    """Variable number (1-based) for 'vertex v is at position i'."""
    return i * n + v + 1


def reduce(instance):
    """Reduce a Clique instance to a SAT instance (both plain dicts)."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Trivial cases, handled directly so that no huge encoding is built.
    if k <= 0:
        # Clique is always yes: an empty CNF is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Clique is always no: the empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Adjacency matrix; edges are undirected.
    adjacent = [[False] * n for _ in range(n)]
    for edge in edges:
        u, v = edge[0], edge[1]
        adjacent[u][v] = True
        adjacent[v][u] = True

    num_vars = k * n
    clauses = []

    # 1. At least one vertex per clique position.
    for i in range(k):
        clauses.append([_variable(i, v, n) for v in range(n)])

    # 2. At most one vertex per clique position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_variable(i, u, n), -_variable(i, v, n)])

    # 3. Chosen vertices at different positions must be adjacent and distinct.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if not adjacent[u][v]:
                        clauses.append([-_variable(i, u, n), -_variable(j, v, n)])

    return {"num_vars": num_vars, "clauses": clauses}

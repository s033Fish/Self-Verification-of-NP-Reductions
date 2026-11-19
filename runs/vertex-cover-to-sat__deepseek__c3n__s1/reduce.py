"""Polynomial-time reduction from Vertex Cover to SAT.

Source: VertexCover instance {"n", "edges", "k"}.
Target: Sat instance {"num_vars", "clauses"}.

Reduction idea
--------------
Introduce one boolean variable per vertex: vertex v (0..n-1) maps to
variable v+1, meaning "v is chosen in the cover".

* For every edge [u, v] add the clause (x_u OR x_v): at least one
  endpoint must be chosen.

* Add an "at most k" cardinality constraint over x_0..x_{n-1}.  This is
  encoded with Sinz's sequential counter, which uses O(n*k) auxiliary
  variables and O(n*k) clauses -- polynomial in the input size.

Edge cases:
* k < 0  -> unsatisfiable formula (empty clause).
* k >= n -> trivially satisfiable formula (all vertices cover everything).
* k == 0 -> just force every x_v to false with unit clauses.
"""

from __future__ import annotations


def _at_most_k_clauses(n: int, k: int, clauses: list[list[int]]) -> int:
    """Append Sinz sequential-counter clauses for sum(x_1..x_n) <= k.

    Variables x_v are 1..n.  Auxiliary variables s(i, j) mean
    "at least j of x_1..x_i are true" and are numbered n+1 ... n+n*k.
    Returns the total number of variables used.
    """
    if k == 0:
        for v in range(1, n + 1):
            clauses.append([-v])
        return n

    def s(i: int, j: int) -> int:
        # i in 1..n, j in 1..k
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
    for i in range(2, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return n + n * k


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no cover can have negative size -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all vertices covers every edge -> trivially satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # 0 <= k < n, hence n >= 1 and k >= 0.
    clauses: list[list[int]] = []

    # Edge clauses: vertex v is variable v+1.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # Cardinality constraint: at most k chosen vertices.
    num_vars = _at_most_k_clauses(n, k, clauses)

    return {"num_vars": num_vars, "clauses": clauses}

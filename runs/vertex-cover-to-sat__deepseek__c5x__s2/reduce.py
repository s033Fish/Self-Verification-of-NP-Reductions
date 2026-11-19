"""Polynomial-time reduction from Vertex Cover to SAT.

SOURCE: VertexCover  instance {"n", "edges", "k"}
TARGET: Sat          instance {"num_vars", "clauses"}

Construction
------------
Introduce one boolean variable x_v (encoded as integer v+1) for every vertex
v in 0..n-1, meaning "v is chosen in the cover".

* For every edge [u, v] add the clause (x_u OR x_v).  These clauses say the
  chosen vertices form a vertex cover.

* Add a CNF encoding of the cardinality constraint "at most k of the x_v are
  true".  We use Sinz's sequential-counter (ladder) encoding, which uses
  O(n*k) auxiliary variables/clauses, hence is polynomial in the input size.

  Auxiliary variable s_{i,j} (for 1 <= i <= n, 1 <= j <= k) means "among
  x_1..x_i at least j are true".  Clauses:

    (not x_i OR s_{i,1})                       for 1 <= i <= n
    (not s_{i-1,1} OR s_{i,1})                 for 2 <= i <= n
    (not x_i OR not s_{i-1,j-1} OR s_{i,j})    for 2 <= i <= n, 2 <= j <= k
    (not s_{i-1,j} OR s_{i,j})                 for 2 <= i <= n, 2 <= j <= k
    (not x_i OR not s_{i-1,k})                 for 2 <= i <= n

Edge cases
----------
* k < 0: answer is always no -> return an unsatisfiable formula (empty clause).
* k >= n: the at-most-k constraint is vacuous (all vertices cover everything),
  so only the edge clauses are needed.
* k == 0: the at-most constraint is just (not x_v) for every v.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover can have negative size -> unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    clauses: list[list[int]] = []

    # Every edge must be covered.
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    # At most k chosen vertices.
    if k >= n:
        # Vacuous: any subset of the n vertices has size <= k.
        return {"num_vars": n, "clauses": clauses}

    if k == 0:
        # No vertex may be chosen.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Sinz sequential counter for "at most k".
    aux: dict[tuple[int, int], int] = {}
    next_var = n + 1
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            aux[(i, j)] = next_var
            next_var += 1
    num_vars = next_var - 1

    for i in range(1, n + 1):
        clauses.append([-i, aux[(i, 1)]])
    for i in range(2, n + 1):
        clauses.append([-aux[(i - 1, 1)], aux[(i, 1)]])
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -aux[(i - 1, j - 1)], aux[(i, j)]])
            clauses.append([-aux[(i - 1, j)], aux[(i, j)]])
    for i in range(2, n + 1):
        clauses.append([-i, -aux[(i - 1, k)]])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from Vertex Cover to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one boolean variable x_v for every vertex v (meaning "v is in the
cover").  For every edge {u, v} add the clause (x_u OR x_v): the cover must
touch every edge.  Then add a cardinality constraint saying that at most k of
the x_v are true.  The cardinality constraint is encoded with Sinz's
sequential-counter (unary counter) encoding, which uses O(n*k) auxiliary
variables and clauses.  Since we only build the counter when 0 <= k < n, we
have k <= n-1 and the encoding is O(n^2) -- polynomial.

Trivial cases are handled directly:
  * k < 0            -> unsatisfiable formula (contains the empty clause).
  * k >= n           -> satisfiable formula (all vertices cover everything).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no vertex cover of negative size exists -> unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # k >= n: taking all vertices is a cover of size n <= k -> satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here 0 <= k <= n-1 (and therefore n >= 1).
    # Variable ids: x_v = v + 1 for v in 0..n-1.
    # Counter variables s(i, j) for i in 1..n, j in 1..k:
    #   s(i, j) means "at least j of x_1..x_i are true".
    num_vars = n + n * k

    def x(v: int) -> int:
        return v + 1

    def s(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    clauses: list[list[int]] = []

    # Every edge must be covered.
    for u, v in edges:
        clauses.append([x(u), x(v)])

    if k == 0:
        # At most zero true variables: every vertex is out of the cover.
        for v in range(n):
            clauses.append([-x(v)])
        return {"num_vars": num_vars, "clauses": clauses}

    # Sinz sequential counter for "at most k of x_1..x_n are true".
    # 1. x_i -> s(i,1)
    for i in range(1, n + 1):
        clauses.append([-x(i - 1), s(i, 1)])
    # 2. s(i-1,1) -> s(i,1)
    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])
    # 3. x_i and s(i-1,j-1) -> s(i,j)
    # 4. s(i-1,j) -> s(i,j)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-x(i - 1), -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])
    # 5. x_i and s(i-1,k) cannot both hold.
    for i in range(2, n + 1):
        clauses.append([-x(i - 1), -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

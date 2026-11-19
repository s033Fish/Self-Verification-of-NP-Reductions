"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce a boolean variable x_v for every vertex v (0 <= v < n), meaning
"v is chosen in the dominating set D".  Number x_v as variable v + 1.

(1) Domination: for every vertex v add the clause

        (x_v  or  x_{u1}  or  ...  or  x_{ud})

    where u1..ud are the neighbours of v.  This clause says v itself or one
    of its neighbours is in D.  Every vertex must be dominated.

(2) Cardinality ("at most k of the x_v are true"): encoded with Sinz's
    sequential counter.  Auxiliary variables s_{i,j} (1 <= i <= n,
    1 <= j <= k) mean "among x_1..x_i at least j are true".  The clauses are

        (not x_i  or  s_{i,1})                       for 1 <= i <= n
        (not s_{i-1,j}  or  s_{i,j})                 for 2 <= i <= n, 1 <= j <= k
        (not x_i  or  not s_{i-1,j-1}  or  s_{i,j})  for 2 <= i <= n, 2 <= j <= k
        (not x_i  or  not s_{i-1,k})                 for 2 <= i <= n

    This uses n*k auxiliary variables and O(n*k) clauses, so the whole
    reduction is polynomial.  It is satisfiable iff at most k of the x_v
    are true.

Edge cases
----------
* k < 0: the answer is always "no"; emit a formula containing the empty
  clause [] (unsatisfiable).
* k >= n: "at most k" is vacuous, so no cardinality clauses are needed.
* k == 0: "at most 0" means every x_v is false; emit unit clauses (not x_v).
* n == 0: no variables and no clauses; the empty formula is satisfiable,
  matching "n = 0 is yes for every k >= 0".
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always "no": a formula with an empty clause is unsatisfiable.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Adjacency lists (undirected, no self loops, no duplicate edges).
    neighbours: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)

    clauses: list[list[int]] = []

    # (1) Every vertex must be dominated.  x_v is variable v + 1.
    for v in range(n):
        clause = [v + 1]
        clause.extend(u + 1 for u in neighbours[v])
        clauses.append(clause)

    # (2) Cardinality constraint "at most k of the x_v are true".
    if k >= n:
        # Vacuous: no cardinality clauses needed.
        num_vars = n
    elif k == 0:
        # At most zero chosen vertices: every x_v must be false.
        num_vars = n
        for v in range(n):
            clauses.append([-(v + 1)])
    else:
        # Sinz sequential counter.  s_{i,j} -> variable n + (i-1)*k + j.
        def s_var(i: int, j: int) -> int:
            # i in 1..n, j in 1..k
            return n + (i - 1) * k + j

        num_vars = n + n * k

        for i in range(1, n + 1):
            xi = i  # variable for vertex i-1 is i
            # (not x_i or s_{i,1})
            clauses.append([-xi, s_var(i, 1)])

        for i in range(2, n + 1):
            xi = i
            for j in range(1, k + 1):
                # (not s_{i-1,j} or s_{i,j})
                clauses.append([-s_var(i - 1, j), s_var(i, j)])
            for j in range(2, k + 1):
                # (not x_i or not s_{i-1,j-1} or s_{i,j})
                clauses.append([-xi, -s_var(i - 1, j - 1), s_var(i, j)])
            # (not x_i or not s_{i-1,k})
            clauses.append([-xi, -s_var(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

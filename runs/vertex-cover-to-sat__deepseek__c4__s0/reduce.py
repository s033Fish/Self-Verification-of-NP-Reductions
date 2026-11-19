"""Polynomial-time reduction from Vertex Cover to SAT.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:          {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Only vertices incident to at least one edge matter for a vertex cover:
isolated vertices never need to be selected.  Let V' be that set, with
n' = |V'| <= 2 * |edges|.  Introduce one boolean variable x_v for every
v in V' (mapped to 1..n'), meaning "v is chosen in the cover".

* For every edge (u, v) add the clause (x_u OR x_v): every edge must be
  covered.
* Add a CNF encoding of "at most k of the x_v are true", using Sinz's
  sequential-counter (ladder) encoding with O(n'*k) auxiliary variables
  and O(n'*k) clauses.  Since k < n' <= 2*|edges| whenever the counter is
  used, the whole output is O(|edges|^2) -- polynomial in the input.

Edge cases:
* k < 0: the answer is always "no"; return a formula containing the empty
  clause, which is unsatisfiable.
* No edges: the empty set covers everything, so the answer is "yes" for
  every k >= 0; return the empty (satisfiable) formula.
* k >= n': "at most k" is vacuous (selecting all incident vertices is
  always allowed), so only the edge clauses are needed.
* k == 0: "at most 0" means every x_v is false; emit unit clauses (-x_v).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always "no": return an unsatisfiable formula.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # No edges: the empty set covers the graph, so it is always "yes".
    if not edges:
        return {"num_vars": 0, "clauses": []}

    # Only vertices incident to some edge can ever be useful.
    vertices = sorted({v for u, v in edges for v in (u, v)})
    nv = len(vertices)
    index = {v: i + 1 for i, v in enumerate(vertices)}

    # Edge clauses: variable index[v] represents vertex v.
    clauses: list[list[int]] = [[index[u], index[v]] for u, v in edges]

    # "At most k" is vacuous when k >= nv (select every incident vertex).
    if k >= nv:
        return {"num_vars": nv, "clauses": clauses}

    # k == 0: all vertices must be unselected.
    if k == 0:
        clauses.extend([-v] for v in range(1, nv + 1))
        return {"num_vars": nv, "clauses": clauses}

    # 1 <= k <= nv-1: Sinz sequential counter for at-most-k.
    # Auxiliary variable s(i, j) means "at least j of x_1..x_i are true",
    # for 1 <= i <= nv and 1 <= j <= k.
    num_vars = nv + nv * k

    def s(i: int, j: int) -> int:
        return nv + (i - 1) * k + j

    # x_i -> s(i, 1)
    for i in range(1, nv + 1):
        clauses.append([-i, s(i, 1)])
    # s(i-1, j) -> s(i, j)
    for i in range(2, nv + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])
    # x_i and s(i-1, j-1) -> s(i, j)
    for i in range(2, nv + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
    # x_i -> not s(i-1, k)   (would exceed k true variables)
    for i in range(2, nv + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}

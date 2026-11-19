"""Polynomial-time reduction from Vertex Cover to SAT.

Source (VertexCover): {"n": n, "edges": [[u, v], ...], "k": k}
Target (Sat):          {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Use one Boolean variable x_v for each vertex v (variable index v+1),
meaning "v is placed in the cover".

* Every edge {u, v} yields the clause (x_u OR x_v): at least one endpoint
  must be selected.

* The bound "at most k selected vertices" is encoded with Sinz's sequential
  counter encoding, which is polynomial: O(n * k) auxiliary variables and
  O(n * k) clauses.  Since the interesting case has 0 <= k < n, this is
  O(n^2) in the input size.

Edge cases are handled directly:
  * k < 0            -> always NO  -> emit an unsatisfiable formula.
  * k >= n           -> always YES -> emit a trivially satisfiable formula.
  * k == 0           -> at most zero vertices: force every x_v false.
"""

from __future__ import annotations

from typing import Any


def _unsat() -> dict[str, Any]:
    # A single empty clause can never be satisfied.
    return {"num_vars": 1, "clauses": [[]]}


def _sat() -> dict[str, Any]:
    # No clauses at all is trivially satisfiable.
    return {"num_vars": 1, "clauses": []}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a SAT instance.

    The returned CNF is satisfiable iff the graph has a vertex cover of size
    at most k.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    k: int = instance["k"]

    # ---- trivial edge cases -------------------------------------------------
    if k < 0:
        return _unsat()
    if k >= n:
        return _sat()

    # From here: 0 <= k < n.
    clauses: list[list[int]] = []

    # Edge constraints: x_u OR x_v  (variable for vertex v is v + 1).
    for u, v in edges:
        clauses.append([u + 1, v + 1])

    if k == 0:
        # At most zero vertices may be chosen: force all x_v false.
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # ---- Sinz sequential counter for "at most k" ---------------------------
    # Auxiliary variable s(i, j) means "at least j of x_1..x_i are true",
    # for 1 <= i <= n and 1 <= j <= k.
    num_vars = n
    s: dict[tuple[int, int], int] = {}
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            num_vars += 1
            s[(i, j)] = num_vars

    for i in range(1, n + 1):
        xi = i  # x_i is variable index i
        # x_i -> s(i, 1)
        clauses.append([-xi, s[(i, 1)]])
        if i >= 2:
            # s(i-1, 1) -> s(i, 1)
            clauses.append([-s[(i - 1, 1)], s[(i, 1)]])
            for j in range(2, k + 1):
                # x_i AND s(i-1, j-1) -> s(i, j)
                clauses.append([-xi, -s[(i - 1, j - 1)], s[(i, j)]])
                # s(i-1, j) -> s(i, j)
                clauses.append([-s[(i - 1, j)], s[(i, j)]])
            # Prevent a (k+1)-th true variable: x_i AND s(i-1, k) is forbidden.
            clauses.append([-xi, -s[(i - 1, k)]])

    return {"num_vars": num_vars, "clauses": clauses}

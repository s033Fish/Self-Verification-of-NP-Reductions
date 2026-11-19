"""Polynomial-time reduction from 3-Coloring to 3-SAT.

SOURCE: {"n": n, "edges": [[u, v], ...]}
TARGET: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable  x(v, c) = 3*v + c + 1  meaning "vertex v has colour c".

* At least one colour per vertex:
      (x(v,0) v x(v,1) v x(v,2))                      for each v
* At most one colour per vertex (2-clauses padded to 3-clauses):
      (~x(v,c) v ~x(v,d))  for c < d
  A 2-clause (a v b) is replaced by (a v b v y) and (a v b v ~y) with a
  fresh variable y.  This is equisatisfiable: if a v b is true both
  clauses hold; if a v b is false both clauses force y and ~y.
* Edge endpoints differ (2-clauses padded the same way):
      (~x(u,c) v ~x(v,c))                             for each edge {u,v}, colour c

Every emitted clause has exactly 3 literals on 3 distinct variables.
The formula is satisfiable iff the graph is 3-colourable.
"""

from __future__ import annotations

from typing import Any


def _x(v: int, c: int) -> int:
    """Variable index (1-based) for 'vertex v has colour c'."""
    return 3 * v + c + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    clauses: list[list[int]] = []
    next_var = 3 * n + 1  # first fresh helper variable

    def pad2(a: int, b: int) -> None:
        """Add 3-clauses equivalent to the 2-clause (a or b)."""
        nonlocal next_var
        y = next_var
        next_var += 1
        clauses.append([a, b, y])
        clauses.append([a, b, -y])

    # At least one colour per vertex (already a proper 3-clause).
    for v in range(n):
        clauses.append([_x(v, 0), _x(v, 1), _x(v, 2)])

    # At most one colour per vertex.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                pad2(-_x(v, c), -_x(v, d))

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            pad2(-_x(u, c), -_x(v, c))

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

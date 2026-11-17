"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Source instance:  {"n": n, "edges": [[u, v], ...]}
Target instance:  {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a variable
    x[v][c]  =  3*v + c + 1          (1-indexed)
meaning "vertex v receives colour c".

* One clause per vertex, [x[v][0], x[v][1], x[v][2]], is already a 1-in-3
  clause: it forces exactly one of the three colours to be true for v.

* For every edge {u, v} and every colour c add a clause
      [x[u][c], x[v][c], z]
  where z is a fresh auxiliary variable.  A 1-in-3 clause is true iff exactly
  one of its three variables is true, so this clause is unsatisfiable when
  both x[u][c] and x[v][c] are true.  When they are not both true it can be
  satisfied by choosing z appropriately (z = true iff both are false).  Hence
  the clause forbids exactly the situation "u and v share colour c".

The number of variables is 3*n + 3*|E| and the number of clauses is
n + 3*|E|, so the reduction runs in linear (hence polynomial) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # x[v][c] is the variable index (1-based) for "vertex v has colour c".
    def x(v: int, c: int) -> int:
        return 3 * v + c + 1

    num_vars = 3 * n
    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            aux = num_vars  # fresh auxiliary variable
            clauses.append([x(u, c), x(v, c), aux])

    return {"num_vars": num_vars, "clauses": clauses}

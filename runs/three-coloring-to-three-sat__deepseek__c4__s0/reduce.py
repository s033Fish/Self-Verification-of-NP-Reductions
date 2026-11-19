"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable

    x_{v,c} = 3*v + c + 1

meaning "vertex v receives colour c".

Clauses
-------
* At least one colour per vertex (already exactly 3 literals on 3 vars):

      (x_{v,0} v x_{v,1} v x_{v,2})

* At most one colour per vertex.  The natural 2-clause
  (~x_{v,c} v ~x_{v,d}) is padded to 3 literals with a single fresh
  variable z; emitting both polarities of z makes the pair equivalent to
  the 2-clause:

      (~x_{v,c} v ~x_{v,d} v  z)
      (~x_{v,c} v ~x_{v,d} v ~z)

* Edge constraints: endpoints of an edge must differ.  For every edge
  (u,v) and colour c, u and v may not both take colour c:

      (~x_{u,c} v ~x_{v,c} v  z)
      (~x_{u,c} v ~x_{v,c} v ~z)

The padding variable z is only needed when there is at least one vertex.
For n = 0 the formula is empty: num_vars = 0, clauses = [] (satisfiable),
matching the source edge case that the empty graph is 3-colourable.

The construction uses O(n^2 + |E|*3) clauses and O(n) variables, so it is
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    def x(v: int, c: int) -> int:
        # Variable for "vertex v has colour c", numbered 1..3n.
        return 3 * v + c + 1

    num_vars = 3 * n
    clauses: list[list[int]] = []

    if n > 0:
        z = 3 * n + 1  # fresh padding variable
        num_vars = 3 * n + 1

        for v in range(n):
            # At least one colour.
            clauses.append([x(v, 0), x(v, 1), x(v, 2)])
            # At most one colour (padded 2-clauses).
            for c in range(3):
                for d in range(c + 1, 3):
                    clauses.append([-x(v, c), -x(v, d), z])
                    clauses.append([-x(v, c), -x(v, d), -z])

        for u, v in edges:
            for c in range(3):
                clauses.append([-x(u, c), -x(v, c), z])
                clauses.append([-x(u, c), -x(v, c), -z])

    return {"num_vars": num_vars, "clauses": clauses}

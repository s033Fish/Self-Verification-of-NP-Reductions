"""Polynomial-time reduction from 3-Coloring to SAT.

SOURCE = ThreeColoring: instance {"n": n, "edges": [[u, v], ...]}
TARGET = Sat: instance {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction (standard):
  For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
  variable x_{v,c}, encoded as the integer 3*v + c + 1 (so variables are
  1..3n).

  Clauses:
    * For each vertex v: (x_{v,0} or x_{v,1} or x_{v,2})
      -- every vertex gets at least one colour.
    * For each edge {u,v} and each colour c: (~x_{u,c} or ~x_{v,c})
      -- the two endpoints of an edge do not share colour c.

  A satisfying assignment of the CNF corresponds exactly to a proper
  3-colouring: the vertex clause forces at least one colour per vertex and
  the edge clauses forbid both endpoints taking the same colour, so each
  vertex effectively has exactly one colour.

  n = 0 yields num_vars = 0 and clauses = [], which is satisfiable, matching
  the fact that the empty graph is 3-colourable.

The construction is O(n + |E|) variables/clauses, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def _var(vertex: int, colour: int) -> int:
    """Positive literal id for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    # Each vertex must receive at least one of the three colours.
    for v in range(n):
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

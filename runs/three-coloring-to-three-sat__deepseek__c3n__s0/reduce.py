"""Polynomial-time reduction from 3-Coloring to 3-SAT.

SOURCE = ThreeColoring: {"n": n, "edges": [[u, v], ...]}
TARGET = ThreeSat:      {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Idea
----
Introduce a boolean variable x_{v,c} for every vertex v and colour c in {0,1,2},
meaning "vertex v receives colour c".  Variable number: 3*v + c + 1.

Constraints:
  * At least one colour per vertex:
        (x_{v,0} or x_{v,1} or x_{v,2})                 -- already 3 literals
  * At most one colour per vertex, for each pair c < d:
        (not x_{v,c} or not x_{v,d})                    -- 2 literals
  * Adjacent vertices differ, for each edge {u,w} and colour c:
        (not x_{u,c} or not x_{w,c})                    -- 2 literals

A binary clause (a or b) is equivalent to
        (a or b or y) and (a or b or not y)
for a fresh variable y.  A *single* fresh variable y may be shared by all the
binary clauses: if every (a or b) holds then any value of y satisfies all
padded clauses; if some (a or b) fails then both its padded clauses are false
for every value of y.  Hence the padding does not change satisfiability.

The resulting formula is satisfiable iff the graph has a proper 3-colouring:
at-least-one plus at-most-one forces exactly one colour per vertex, and the
edge clauses force adjacent vertices to differ.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    def var(v: int, c: int) -> int:
        """Variable for 'vertex v has colour c' (c in 0..2)."""
        return 3 * v + c + 1

    clauses: list[list[int]] = []

    # At least one colour per vertex (already exactly 3 literals).
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Single fresh variable used to pad every binary clause to length 3.
    pad = 3 * n + 1

    def add_binary(a: int, b: int) -> None:
        """Add clauses equivalent to the binary clause (a or b)."""
        clauses.append([a, b, pad])
        clauses.append([a, b, -pad])

    # At most one colour per vertex.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                add_binary(-var(v, c), -var(v, d))

    # Adjacent vertices must receive different colours.
    for u, w in edges:
        for c in range(3):
            add_binary(-var(u, c), -var(w, c))

    # If there are no clauses (n == 0) the empty formula is satisfiable with 0
    # variables; otherwise the padding variable is the largest variable used.
    num_vars = pad if clauses else 0
    return {"num_vars": num_vars, "clauses": clauses}

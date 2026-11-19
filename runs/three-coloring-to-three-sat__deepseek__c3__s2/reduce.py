"""Polynomial-time reduction from 3-Coloring to 3-SAT.

SOURCE instance: {"n": n, "edges": [[u, v], ...]}
TARGET instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in 0..2 introduce the boolean
variable x_{v,c}, meaning "vertex v receives colour c".  Numbering:
    x_{v,c} = 3*v + c + 1        (so variables are 1..3n)

Clauses:
  * For each vertex v:  (x_{v,0} OR x_{v,1} OR x_{v,2})
        -- every vertex gets at least one colour.
  * For each vertex v and colour pair c1 < c2:
        (NOT x_{v,c1} OR NOT x_{v,c2})
        -- every vertex gets at most one colour.
  * For each edge {u, w} and colour c:
        (NOT x_{u,c} OR NOT x_{w,c})
        -- adjacent vertices do not share a colour.

The "at most one" and edge constraints are two-literal clauses, while the
target requires exactly three literals on three distinct variables.  Each
two-literal clause (a OR b) is therefore replaced by the pair
    (a OR b OR p), (a OR b OR NOT p)
using one shared fresh variable p.  A single shared p suffices: if (a OR b)
holds, both clauses are satisfied whatever p is; if (a OR b) fails, the pair
forces p and NOT p, i.e. unsatisfiable.  Hence the pair is equivalent to
(a OR b), and sharing p across all padded clauses preserves equivalence.

Correctness
-----------
A proper 3-colouring yields a satisfying assignment by setting exactly the
x_{v,c} matching each vertex's colour (p arbitrary).  Conversely, any
satisfying assignment has at least one true x_{v,c} per vertex (at-least-one
clause) and at most one (padded pairwise clauses), hence exactly one, so it
defines a colouring; edge clauses then force adjacent vertices to differ.

The construction uses 3n + 1 variables and O(n + |E|) clauses, so it runs in
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to an equisatisfiable 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def var(v: int, c: int) -> int:
        # Variable for "vertex v has colour c", numbered 1..3n.
        return 3 * v + c + 1

    clauses: list[list[int]] = []

    # Every vertex gets at least one colour (already a 3-literal clause).
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Two-literal constraints, padded to three literals below.
    two_literal: list[list[int]] = []

    # Every vertex gets at most one colour.
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                two_literal.append([-var(v, c1), -var(v, c2)])

    # Adjacent vertices get different colours.
    for u, w in edges:
        for c in range(3):
            two_literal.append([-var(u, c), -var(w, c)])

    num_vars = 3 * n
    if two_literal:
        pad = num_vars + 1  # one shared fresh padding variable
        num_vars += 1
        for a, b in two_literal:
            clauses.append([a, b, pad])
            clauses.append([a, b, -pad])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Source instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Target instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour c in {0, 1, 2} introduce a boolean variable
colour(v, c) meaning "vertex v receives colour c".  The positive 1-in-3
clause

    (colour(v, 0), colour(v, 1), colour(v, 2))

says that exactly one of the three colour variables of v is true, i.e. v
receives exactly one colour.

For every edge {u, v} and every colour c we must forbid both endpoints
receiving colour c.  Introduce a fresh auxiliary variable aux(e, c) and
the positive 1-in-3 clause

    (colour(u, c), colour(v, c), aux(e, c)).

This clause is satisfiable exactly when colour(u, c) and colour(v, c) are
not both true: if both are true the clause would contain at least two
true variables; if at most one is true the auxiliary variable can be set
to make the number of true variables exactly one.  Each auxiliary
variable occurs in exactly one clause, so it imposes no other
restriction.

Therefore the produced formula is satisfiable iff the graph admits a
proper 3-colouring.  It has 3n + 3|E| variables and n + 3|E| clauses, so
the construction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 0
    clauses: list[list[int]] = []

    # colour(v, c) -> variable number
    colour: dict[tuple[int, int], int] = {}
    for v in range(n):
        for c in range(3):
            num_vars += 1
            colour[(v, c)] = num_vars

    # Every vertex gets exactly one colour.
    for v in range(n):
        clauses.append([colour[(v, 0)], colour[(v, 1)], colour[(v, 2)]])

    # For every edge and colour, forbid the endpoints sharing that colour.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            aux = num_vars
            clauses.append([colour[(u, c)], colour[(v, c)], aux])

    return {"num_vars": num_vars, "clauses": clauses}

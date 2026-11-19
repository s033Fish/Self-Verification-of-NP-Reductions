"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 and every colour c in {0, 1, 2}, introduce a
Boolean variable x(v, c), numbered 3*v + c + 1.  It is true exactly when
vertex v receives colour c.

Clauses:
  * At least one colour for v:        [x(v,0), x(v,1), x(v,2)]
  * At most one colour for v:         [-x(v,c), -x(v,d)] for c < d
  * Edge endpoints differ, colour c:  [-x(u,c), -x(v,c)] for each edge [u,v]

A satisfying assignment chooses exactly one colour per vertex, and the edge
clauses forbid both endpoints of an edge from sharing a colour.  Conversely
any proper 3-colouring extends to a satisfying assignment by setting x(v,c)
true iff v has colour c.  Hence the target formula is satisfiable iff the
source graph is 3-colourable.

The construction uses O(n + |E|) variables/clauses and runs in polynomial
time.  It never calls a solver.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]

_COLOURS = (0, 1, 2)


def _var(vertex: int, colour: int) -> int:
    """1-based SAT variable for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: Instance) -> Instance:
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    for v in range(n):
        # Each vertex must receive at least one colour.
        clauses.append([_var(v, c) for c in _COLOURS])
        # Each vertex must receive at most one colour.
        for i in range(len(_COLOURS)):
            for j in range(i + 1, len(_COLOURS)):
                clauses.append([-_var(v, _COLOURS[i]), -_var(v, _COLOURS[j])])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in _COLOURS:
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance (ThreeColoring):
    {"n": n, "edges": [[u, v], ...]}
Target instance (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0, 1, 2} introduce a Boolean
variable x_{v,c} meaning "vertex v has colour c".  Number the variables

    var(v, c) = 3 * v + c + 1        (so variables are 1..3n)

and add the following clauses:

  * for each vertex v:            (x_{v,0} v x_{v,1} v x_{v,2})
        at least one colour is chosen for v;
  * for each vertex v and c < d:  (~x_{v,c} v ~x_{v,d})
        at most one colour is chosen for v;
  * for each edge {u, v} and c:   (~x_{u,c} v ~x_{v,c})
        the two endpoints of an edge do not share colour c.

A satisfying assignment of the formula corresponds exactly to a proper
3-colouring of the graph (the "at least one" clause forces a colour, the
"at most one" clauses make it unique, and the edge clauses forbid equal
colours on adjacent vertices), and vice versa.  Hence the formula is
satisfiable iff the graph is 3-colourable.

The construction uses O(n + |E|) variables/clauses and runs in polynomial
time.  It never calls a brute-force solver.
"""

from __future__ import annotations

from typing import Any


def _var(vertex: int, colour: int) -> int:
    """Variable index (1-based) for 'vertex has colour'."""
    return 3 * vertex + colour + 1


def reduce(instance: Any) -> dict:
    """Reduce a 3-Coloring instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    for v in range(n):
        # At least one colour for v.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour for v.
        clauses.append([-_var(v, 0), -_var(v, 1)])
        clauses.append([-_var(v, 0), -_var(v, 2)])
        clauses.append([-_var(v, 1), -_var(v, 2)])

    for edge in edges:
        u, v = edge[0], edge[1]
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

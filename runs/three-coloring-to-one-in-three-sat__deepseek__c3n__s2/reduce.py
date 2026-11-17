"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}  (graph 3-colorability)
Target instance: {"num_vars": m, "clauses": [[a, b, c], ...]}  (positive 1-in-3-SAT)

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a variable
    x(v, c) = 3*v + c + 1
meaning "vertex v gets colour c".

For every vertex v add the clause
    [x(v,0), x(v,1), x(v,2)]
which is true under an assignment iff EXACTLY ONE of the three variables is
true, i.e. every vertex gets exactly one colour.

For every edge e = (u, v) (index i) and every colour c introduce a fresh
auxiliary variable
    a(i, c) = 3*n + 3*i + c + 1
and add the clause
    [x(u,c), x(v,c), a(i,c)].

Because a(i,c) occurs in no other clause it can be chosen freely: the clause
is satisfiable unless both x(u,c) and x(v,c) are true (then it would contain
two true variables).  Hence the clause exactly forbids u and v sharing colour
c.  Since every colour is forbidden for an edge, adjacent vertices must get
different colours.

Therefore the formula is satisfiable iff the graph is 3-colourable.

Size: 3*n + 3*|E| variables and n + 3*|E| clauses, all produced in linear time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a positive 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n + 3 * len(edges)
    clauses: list[list[int]] = []

    # Each vertex gets exactly one of its three colour variables true.
    for v in range(n):
        base = 3 * v
        clauses.append([base + 1, base + 2, base + 3])

    # Each edge forbids the two endpoints from sharing a colour.
    for i, edge in enumerate(edges):
        u, v = edge
        aux_base = 3 * n + 3 * i
        for c in range(3):
            clauses.append([3 * u + c + 1, 3 * v + c + 1, aux_base + c + 1])

    return {"num_vars": num_vars, "clauses": clauses}

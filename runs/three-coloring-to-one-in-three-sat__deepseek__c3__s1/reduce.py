"""Polynomial-time reduction from 3-Coloring to 1-in-3-SAT.

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x[v][c] meaning "vertex v has colour c".  Number them

    x(v, c) = 3*v + c + 1          (so variables 1 .. 3n)

* Vertex gadget: the clause [x(v,0), x(v,1), x(v,2)] says exactly one of the
  three colour variables of v is true, i.e. v gets exactly one colour.

* Edge gadget: for an edge (u, v) and each colour c, add a fresh auxiliary
  variable a and the clause [x(u,c), x(v,c), a].  A 1-in-3 clause is satisfied
  iff exactly one of its three variables is true, so this forbids x(u,c) and
  x(v,c) from being simultaneously true (if both were true the clause would
  have >= 2 true variables; if at most one is true we can set a to make it
  exactly one).  Hence u and v cannot share any colour, i.e. they differ.

Correctness
-----------
If the graph is 3-colourable, colour it properly, set x(v,c) true iff v has
colour c, and set each auxiliary variable true iff both x(u,c), x(v,c) are
false.  Every clause then has exactly one true variable.

Conversely, any satisfying assignment has exactly one colour per vertex
(vertex clauses) and, for every edge and colour c, not both endpoints have
colour c (edge clauses), so the induced colouring is a proper 3-colouring.

Edge cases: n = 0 gives num_vars = 0 and no clauses (yes).  Any graph with
n >= 1 produces at least one clause over 3 distinct variables, so num_vars
>= 3 as required.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a 3-Coloring instance to a 1-in-3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: list[list[int]] = []

    def x(vertex: int, colour: int) -> int:
        return 3 * vertex + colour + 1

    # Vertex gadget: exactly one colour per vertex.
    for v in range(n):
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

    # Edge gadget: endpoints must not share a colour.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            aux = num_vars
            clauses.append([x(u, c), x(v, c), aux])

    return {"num_vars": num_vars, "clauses": clauses}

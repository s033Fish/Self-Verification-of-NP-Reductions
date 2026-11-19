"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Use three colours: T = 0, F = 1, B = 2.

* A base triangle on vertices 0, 1, 2 forces them to receive the three
  distinct colours; think of vertex 2 as the "base" colour B and 0/1 as
  the truth colours.

* For every variable v (1..m) add two vertices p_v and n_v, joined to
  each other and both joined to the base vertex B.  Hence p_v and n_v
  must take the two truth colours, and they are opposite: p_v is the
  colour of literal +v and n_v the colour of literal -v.

* For every clause (l1, l2, l3) add a fresh triangle a, b, c and join the
  vertex representing li to the i-th triangle vertex.  Since a, b, c are
  pairwise adjacent they must get three distinct colours.  If all three
  literals had the same colour, each triangle vertex would have to avoid
  that one colour, leaving only two colours for three pairwise adjacent
  vertices -- impossible.  If the literals are not all equal, distinct
  colours for a, b, c avoiding the respective literals always exist (one
  colour is unused by the three literals, and it can be assigned to the
  triangle vertex whose literal has the repeated colour).  So the gadget
  is 3-colourable exactly when the clause is not-all-equal.

The graph is 3-colourable iff the formula is NAE-satisfiable.  The
construction uses O(m + k) vertices and edges, so it is polynomial.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]

T, F, B = 0, 1, 2


def reduce(instance: Instance) -> Instance:
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: vertices 0 (T), 1 (F), 2 (B).
    edges: list[list[int]] = [[0, 1], [0, 2], [1, 2]]

    def literal_vertex(literal: int) -> int:
        # Variable v occupies vertices 3 + 2*(v-1) (positive) and +1 (negative).
        base = 3 + 2 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        pos = 3 + 2 * (v - 1)
        neg = pos + 1
        edges.append([pos, neg])
        edges.append([pos, B])
        edges.append([neg, B])

    # Clause gadgets.
    n = 3 + 2 * num_vars
    for clause in clauses:
        a, b, c = n, n + 1, n + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        for literal, vertex in zip(clause, (a, b, c)):
            edges.append([literal_vertex(literal), vertex])
        n += 3

    return {"n": n, "edges": edges}

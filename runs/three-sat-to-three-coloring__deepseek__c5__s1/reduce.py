"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Construction
------------
Vertices 0, 1, 2 form a triangle and act as the three colours:
    0 -> True, 1 -> False, 2 -> Base
Because they are mutually adjacent they must receive three distinct colours,
so we can (and do) name their colours True/False/Base.

For every variable v in 1..m we add two vertices:
    pos(v) and neg(v)
and the edges
    pos(v) -- neg(v),   pos(v) -- 2,   neg(v) -- 2.
Both are adjacent to Base (vertex 2), so neither can be Base; they are
adjacent to each other, so exactly one of them is True and the other False.
This is the standard variable gadget.

For every clause (l1, l2, l3) we add six fresh vertices
    w1, w2, w3, t1, t2, t3
and the edges
    wi -- lit(li)          (lit(+v) = pos(v), lit(-v) = neg(v))
    wi -- 0                (vertex 0 is the fixed True-coloured vertex)
    ti -- wi
    t1 -- t2, t2 -- t3, t3 -- t1      (a triangle)

Claim: this clause gadget is 3-colourable (with the literal vertices already
coloured True/False and vertex 0 coloured True) iff at least one literal is
True.
  * If every literal is False (colour 1): each wi is adjacent to a False
    literal and to True (vertex 0), so wi must be Base (colour 2).  Then each
    ti is adjacent to a Base vertex and must avoid colour 2, so ti is True or
    False; a triangle on t1, t2, t3 cannot be coloured with only two colours.
    Impossible.
  * If some literal is True (colour 0), say l1: set w1 = False (colour 1),
    w2 = w3 = Base (colour 2) -- always legal, because each wi only has to
    differ from its literal and from True.  Then colour the triangle
    t1 = Base (2), t2 = True (0), t3 = False (1); t1 avoids w1 = False, and
    t2, t3 avoid w2 = w3 = Base.  Valid.

The gadgets only share the literal vertices, so a satisfying assignment extends
to a proper 3-colouring and conversely every proper 3-colouring restricts to a
satisfying assignment.  Hence the formula is satisfiable iff the graph is
3-colourable.

The graph has 3 + 2*m + 6*k vertices and 3 + 3*m + 12*k edges, so the
construction is polynomial (linear) in the input size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a 3-Coloring instance.

    Input:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output: {"n": n, "edges": [[u, v], ...]}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: 0 = True, 1 = False, 2 = Base.
    TRUE, FALSE, BASE = 0, 1, 2
    edges: list[list[int]] = [[TRUE, FALSE], [FALSE, BASE], [TRUE, BASE]]
    n = 3

    # Variable gadgets.
    pos = {}  # variable -> vertex meaning "variable is True"
    neg = {}  # variable -> vertex meaning "variable is False"
    for v in range(1, num_vars + 1):
        p = n
        q = n + 1
        n += 2
        pos[v] = p
        neg[v] = q
        edges.append([p, q])
        edges.append([p, BASE])
        edges.append([q, BASE])

    def literal_vertex(literal: int) -> int:
        v = abs(literal)
        return pos[v] if literal > 0 else neg[v]

    # Clause gadgets.
    for clause in clauses:
        w1, w2, w3 = n, n + 1, n + 2
        t1, t2, t3 = n + 3, n + 4, n + 5
        n += 6
        for w, literal in zip((w1, w2, w3), clause):
            edges.append([w, literal_vertex(literal)])
            edges.append([w, TRUE])
        edges.append([t1, w1])
        edges.append([t2, w2])
        edges.append([t3, w3])
        edges.append([t1, t2])
        edges.append([t2, t3])
        edges.append([t3, t1])

    return {"n": n, "edges": edges}

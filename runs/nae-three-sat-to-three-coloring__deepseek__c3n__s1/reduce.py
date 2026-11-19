"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction
------------
Colours are {0, 1, 2}.  We build a graph whose proper 3-colourings encode
truth assignments.

* Base triangle on vertices B=0, T=1, F=2.  It forces the three colours to
  be distinct; we interpret colour(T) as "true" and colour(F) as "false".

* For every variable v in 1..m create two vertices x_v and n_v joined by an
  edge, and join both of them to B.  Hence x_v and n_v receive the two
  colours different from colour(B), i.e. colour(T) and colour(F), in some
  order.  Reading colour(x_v) == colour(T) as "v is true" makes x_v the
  vertex of literal +v and n_v the vertex of literal -v.

* For every clause (l1, l2, l3) create a fresh triangle p, q, r and add the
  edges (lit(l1), p), (lit(l2), q), (lit(l3), r), where lit(l) is the vertex
  of literal l.

  Claim: this triangle gadget is 3-colourable iff the three literal colours
  are not all equal.
  - If all three are equal, p, q, r are each forbidden one and the same
    colour, so they can use only the other two colours, but being a triangle
    they must be pairwise distinct: impossible.
  - If not all equal, a valid colouring exists (e.g. for colours a,b,c with
    a=b!=c choose p=c, q=the third colour, r=a; the other cases are
    symmetric).

Therefore the whole graph is 3-colourable iff there is a truth assignment
making every clause not-all-equal, i.e. iff the NAE-3-SAT instance is yes.

The construction uses O(m + #clauses) vertices and edges, so it runs in
polynomial time.
"""

from __future__ import annotations

from problems import NaeThreeSat, ThreeColoring


def reduce(instance: dict) -> dict:
    """Reduce a NAE-3-SAT instance to a 3-Coloring instance."""
    NaeThreeSat.validate(instance)

    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[tuple[int, int]] = []

    def add(u: int, v: int) -> None:
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # Base triangle: 0 = B, 1 = T, 2 = F.
    add(0, 1)
    add(1, 2)
    add(0, 2)

    def lit_vertex(literal: int) -> int:
        base = 3 + 2 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    # Variable gadgets.
    for v in range(1, m + 1):
        x = 3 + 2 * (v - 1)
        nx = x + 1
        add(x, nx)
        add(x, 0)
        add(nx, 0)

    next_vertex = 3 + 2 * m

    # Clause gadgets.
    for clause in clauses:
        p, q, r = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        add(p, q)
        add(q, r)
        add(p, r)
        add(lit_vertex(clause[0]), p)
        add(lit_vertex(clause[1]), q)
        add(lit_vertex(clause[2]), r)

    # Keep the graph simple (no duplicate edges).
    seen: set[tuple[int, int]] = set()
    deduped: list[list[int]] = []
    for u, v in edges:
        if (u, v) not in seen:
            seen.add((u, v))
            deduped.append([u, v])

    result = {"n": next_vertex, "edges": deduped}
    ThreeColoring.validate(result)
    return result

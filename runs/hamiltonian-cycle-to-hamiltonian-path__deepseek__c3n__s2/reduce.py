"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given a source graph G = (V, E) with n = |V| vertices:

* If n <= 2 the source answer is always "no" (a simple graph needs at
  least 3 vertices for a cycle).  We return the fixed no-instance of the
  target, {"n": 0, "edges": []} (an empty graph has no Hamiltonian path).

* Otherwise pick a vertex v (we use v = 0) and build H as follows.
  Delete v, keep every remaining vertex and every edge not incident to v.
  Add four fresh vertices v1, v2, a, b:
      - v1 and v2 are both joined to every neighbour of v,
      - a is joined only to v1,
      - b is joined only to v2.

Claim: G has a Hamiltonian cycle  <=>  H has a Hamiltonian path.

(=>) If v - u - ... - w - v is a Hamiltonian cycle of G, then
     a - v1 - u - ... - w - v2 - b is a Hamiltonian path of H.

(<=) In H, a and b have degree 1, so every Hamiltonian path of H must
     start at a and end at b:  a - v1 - u - ... - w - v2 - b, with
     u, w in N(v).  Removing a, v1, v2, b leaves a Hamiltonian path of
     G - v from u to w, hence v - u - ... - w - v is a Hamiltonian cycle
     of G.

The construction is clearly polynomial (linear) in the size of the input.
"""

from __future__ import annotations


def reduce(instance):
    """Return a HamiltonianPath instance equivalent to the given
    HamiltonianCycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: source is always a no-instance; return a target no-instance.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0

    # Relabel the surviving vertices of G - v into 0..n-2.
    def relabel(u: int) -> int:
        return u - 1 if u > v else u

    # Neighbours of v in G.
    neighbours = set()
    for u, w in edges:
        if u == v:
            neighbours.add(w)
        elif w == v:
            neighbours.add(u)

    # Fresh vertices.
    v1 = n - 1
    v2 = n
    a = n + 1
    b = n + 2

    new_edges = []
    seen = set()

    def add(x: int, y: int) -> None:
        if x == y:
            return
        key = (x, y) if x < y else (y, x)
        if key not in seen:
            seen.add(key)
            new_edges.append([x, y])

    # Edges of G not incident to v.
    for u, w in edges:
        if u == v or w == v:
            continue
        add(relabel(u), relabel(w))

    # v1, v2 attached to every neighbour of v.
    for u in neighbours:
        add(v1, relabel(u))
        add(v2, relabel(u))

    # Pendants forcing v1 and v2 to be path endpoints.
    add(a, v1)
    add(b, v2)

    return {"n": n + 3, "edges": new_edges}

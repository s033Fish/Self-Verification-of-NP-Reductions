r"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given a source instance G = (V, E) with V = {0, ..., n-1}:

* If n <= 2, G has no Hamiltonian cycle (a simple graph needs >= 3
  vertices), so return a target instance that is certainly "no":
  {"n": 0, "edges": []}   (n = 0 is "no" for Hamiltonian Path).

* Otherwise fix the vertex v = 0 and build G' as follows.  Keep the
  vertices 1..n-1 (relabelled to 0..n-2), and add four new vertices:

      v1 = n-1   (a "copy" of v, adjacent to every neighbour of v)
      v2 = n     (a second "copy" of v, adjacent to every neighbour of v)
      p1 = n+1   (a pendant leaf attached only to v1)
      p2 = n+2   (a pendant leaf attached only to v2)

  Edges of G' are:
      * every edge of G not incident to v (relabelled),
      * for each neighbour u of v:  {u, v1} and {u, v2},
      * the two pendant edges {v1, p1} and {v2, p2}.

Correctness
-----------
(=>) A Hamiltonian cycle of G through v looks like v, a, ..., b, v.
     Then p1, v1, a, ..., b, v2, p2 is a Hamiltonian path of G'.

(<=) In any Hamiltonian path of G', the leaves p1 and p2 have degree 1,
     hence must be the two endpoints.  The path is therefore
     p1, v1, x1, ..., xk, v2, p2 with {x1, ..., xk} = V \ {v}.  Since
     v1 (resp. v2) is adjacent exactly to the neighbours of v, x1 and xk
     are neighbours of v in G, and x1, ..., xk is a Hamiltonian path of
     G - v.  As n >= 3 we have k = n-1 >= 2, so x1 != xk, and
     v, x1, ..., xk, v is a Hamiltonian cycle of G.

The construction is clearly polynomial (linear in |V| + |E|).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no Hamiltonian cycle exists; emit a trivially "no" target.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0
    new_n = n + 3
    v1 = n - 1
    v2 = n
    p1 = n + 1
    p2 = n + 2

    new_edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()

    def add(a: int, b: int) -> None:
        if a > b:
            a, b = b, a
        if (a, b) not in seen:
            seen.add((a, b))
            new_edges.append([a, b])

    for u, w in edges:
        if u == v or w == v:
            continue
        # relabel original vertices 1..n-1 to 0..n-2
        add(u - 1, w - 1)

    for u, w in edges:
        if u == v:
            nb = w
        elif w == v:
            nb = u
        else:
            continue
        add(nb - 1, v1)
        add(nb - 1, v2)

    add(v1, p1)
    add(v2, p2)

    return {"n": new_n, "edges": new_edges}

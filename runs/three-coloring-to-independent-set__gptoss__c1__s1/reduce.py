"""Reduction from 3-Coloring to Independent Set.

The source problem is ``ThreeColoring`` with instances of the form

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered ``0 .. n-1``.

The target problem is ``IndependentSet`` with instances of the form

    {"n": N, "edges": [[u, v], ...], "k": k}

The reduction constructs a new graph H that contains three copies of each
original vertex – one for each colour.  An independent set of size ``n`` in
H corresponds exactly to a proper 3‑colouring of the original graph.

Construction (standard textbook reduction):

* For every original vertex ``v`` create three vertices ``(v,0)``, ``(v,1)``
  and ``(v,2)`` in H.  They are numbered ``v*3 + c`` where ``c`` is the colour
  index.
* For each original edge ``(u, v)`` add edges between the colour‑copies that
  would represent the same colour, i.e. ``(u,c) – (v,c)`` for ``c = 0,1,2``.
  This forbids adjacent vertices from receiving the same colour.
* For each original vertex ``v`` add a triangle between its three colour
  vertices.  This ensures that an independent set can contain at most one of
  those three vertices – selecting more would correspond to assigning two
  colours to the same vertex.

The resulting graph has ``N = 3 * n`` vertices and we ask for an independent
set of size ``k = n``.  It is easy to verify:

* If G is 3‑colourable, choose for each vertex ``v`` the vertex ``(v, colour)``
  that matches its colour.  No two chosen vertices are adjacent, so they form
  an independent set of size ``n``.
* Conversely, any independent set of size ``n`` must contain exactly one
  colour‑vertex for each original vertex (because the three colour vertices
  of a vertex form a triangle).  The colours assigned this way give a proper
  3‑colouring of G.

The reduction runs in polynomial time – O(n + |E|).
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs) describing the input graph.

    Returns
    -------
    dict
        An IndependentSet instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Number of vertices in the constructed graph: three copies per original.
    N = 3 * n
    edges: List[List[int]] = []

    # Helper to map (vertex, colour) -> index in the new graph.
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add edges that prevent adjacent vertices from sharing the same colour.
    for u, v in original_edges:
        for colour in range(3):
            a = idx(u, colour)
            b = idx(v, colour)
            # Store edge with smaller vertex first for consistency.
            if a < b:
                edges.append([a, b])
            else:
                edges.append([b, a])

    # 2. Add a triangle among the three colour vertices of each original vertex.
    for v in range(n):
        c0 = idx(v, 0)
        c1 = idx(v, 1)
        c2 = idx(v, 2)
        edges.append([c0, c1])
        edges.append([c0, c2])
        edges.append([c1, c2])

    # The target asks for an independent set of size exactly n.
    k = n

    return {"n": N, "edges": edges, "k": k}


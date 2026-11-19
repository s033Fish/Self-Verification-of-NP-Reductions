"""Reduction from 3-Coloring to Independent Set.

The source problem is *ThreeColoring* with instances of the form

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered 0 … n‑1.  The target problem is *IndependentSet*
with instances

    {"n": N, "edges": [[u, v], ...], "k": k}

The reduction creates a new graph H that has a vertex for every pair
``(original_vertex, colour)`` where colour ∈ {0,1,2}.  H contains three
vertices for each original vertex, giving ``N = 3 * n``.  An independent set
of size at least ``k = n`` in H corresponds exactly to a proper 3‑colouring
of the original graph:

* For each original vertex v we add a triangle between its three colour
  vertices so that an independent set can contain **at most one** of them.
* For each edge (u, v) in the original graph we add edges between the
  colour‑i vertices of u and v for every colour i.  This forbids two
  adjacent original vertices from receiving the same colour.

If the original graph is 3‑colourable, we can pick for each vertex the
vertex representing its colour; these n vertices are pairwise non‑adjacent,
yielding an independent set of size n.  Conversely, any independent set of
size n must contain exactly one colour‑vertex for each original vertex (the
triangle edges prevent more than one, and the total size forces at least one
per original vertex).  The selected vertices give a proper 3‑colouring.

Thus the instance ``{"n": n, "edges": E}`` is a YES instance of 3‑Coloring
iff the constructed instance ``{"n": 3*n, "edges": H_edges, "k": n}``
is a YES instance of Independent Set.

The construction runs in polynomial time (linear in the size of the input
graph).
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs) describing the input graph.

    Returns
    -------
    dict
        An IndependentSet instance ``{"n": 3*n, "edges": ..., "k": n}``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Number of vertices in the new graph: three copies (one per colour).
    N = 3 * n
    k = n

    edges: List[List[int]] = []

    # Helper to compute the id of (vertex, colour).
    def vid(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. For each original vertex, add a triangle among its three colour
    #    vertices to enforce that at most one colour can be chosen.
    for v in range(n):
        a = vid(v, 0)
        b = vid(v, 1)
        c = vid(v, 2)
        edges.append([a, b])
        edges.append([a, c])
        edges.append([b, c])

    # 2. For each original edge (u, v), forbid using the same colour on both
    #    endpoints by connecting the corresponding colour vertices.
    for u, v in original_edges:
        for colour in range(3):
            edges.append([vid(u, colour), vid(v, colour)])

    # The format expects undirected edges; the construction already avoids
    # duplicates because each pair is added exactly once.
    return {"n": N, "edges": edges, "k": k}

# The module is intended to be imported by the evaluation harness; no
# top‑level testing code is included to keep the file minimal.

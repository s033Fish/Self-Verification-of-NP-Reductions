"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` (graph 3‑colorability).
The target problem is :class:`IndependentSet`.

For a given graph G = (V, E) we construct a graph H as follows:

* For each vertex v ∈ V we create three vertices (v,0), (v,1), (v,2).
  These three vertices form a triangle, ensuring that an independent set
  can contain **at most one** of them.
* For each edge {u,v} ∈ E and each colour c ∈ {0,1,2} we add an edge
  between (u,c) and (v,c).  This forbids the independent set from picking
  the same colour for adjacent original vertices.

An independent set of size |V| in H corresponds exactly to a proper
3‑colouring of G: pick the unique vertex from each triangle – its colour
is the colour assigned to the original vertex.  Conversely, any proper
3‑colouring yields such an independent set.

The reduction runs in O(|V| + |E|) time and produces a graph with 3|V|
vertices and 3|V| + 3|E| edges.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation helpers.
from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑Coloring instance, i.e. ``{"n": n,
        "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": 3*n, "edges": [...], "k": n}``.
    """
    # Validate the source instance – this will raise InvalidInstance if malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]

    # New graph parameters.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # Helper to compute the id of (vertex, colour).
    def vid(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add the triangle edges for each original vertex.
    for v in range(n):
        a = vid(v, 0)
        b = vid(v, 1)
        c = vid(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid equal colours.
    for u, v in original_edges:
        for colour in range(3):
            new_edges.append([vid(u, colour), vid(v, colour)])

    # The target asks for an independent set of size at least n.
    target_instance: Dict[str, Any] = {"n": new_n, "edges": new_edges, "k": n}

    # Validate the produced target instance (optional but helpful for debugging).
    IndependentSet.validate(target_instance)
    return target_instance

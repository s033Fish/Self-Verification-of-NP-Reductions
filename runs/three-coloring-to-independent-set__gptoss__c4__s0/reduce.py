"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`IndependentSet` defined in the same file.

Given a graph G = (V, E) we construct a new graph H = (V', E') such that
G is 3‑colorable iff H contains an independent set of size |V|.

Construction (standard textbook reduction):

* For each vertex v ∈ V we create three vertices (v,0), (v,1), (v,2) in V'.
  These represent the choice of colour 0, 1 or 2 for v.
* For each original vertex v we add a triangle between its three copies –
  this forces an independent set to pick at most one of them.
* For each original edge {u, v} ∈ E we add edges connecting the copies of the
  same colour, i.e. (u,c) – (v,c) for c = 0,1,2.  This prevents the independent
  set from picking the same colour for adjacent vertices.

If G has a proper 3‑colouring, selecting the vertex (v, colour(v)) for each v
forms an independent set of size |V| in H.  Conversely, any independent set of
size |V| must contain exactly one copy of each original vertex (otherwise the
size would be < |V| because of the triangles) and the colours of those copies
yield a proper 3‑colouring of G.

The reduction runs in O(|V| + |E|) time and produces a graph with 3|V| vertices
and at most 3|V| + 3|E| edges.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A valid instance of :class:`ThreeColoring` – a dict with keys ``n``
        (number of vertices) and ``edges`` (list of ``[u, v]`` pairs).

    Returns
    -------
    dict
        A valid instance of :class:`IndependentSet`.  The returned graph has
        ``3 * n`` vertices and ``k = n``.  The edges are constructed as
        described in the module docstring.
    """
    # Validate the source instance (will raise if malformed).
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]

    # Mapping: (v, colour) -> new vertex id in the target graph.
    # We simply number them consecutively: id = v * 3 + colour, where colour∈{0,1,2}.
    def node_id(v: int, colour: int) -> int:
        return v * 3 + colour

    target_n = n * 3
    target_edges: List[List[int]] = []

    # 1. Add the triangle for each original vertex.
    for v in range(n):
        a, b, c = node_id(v, 0), node_id(v, 1), node_id(v, 2)
        target_edges.append([a, b])
        target_edges.append([a, c])
        target_edges.append([b, c])

    # 2. For each original edge, forbid same colour on both endpoints.
    for u, v in original_edges:
        for colour in range(3):
            target_edges.append([node_id(u, colour), node_id(v, colour)])

    # Build the target instance.
    target_instance = {
        "n": target_n,
        "edges": target_edges,
        "k": n,
    }

    # Validate the produced instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance


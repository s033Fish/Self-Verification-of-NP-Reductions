"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` and the target problem is
`IndependentSet`.  Given a graph G = (V, E) we construct a new graph H as
follows:

* For each vertex v ∈ V we create three vertices (v,0), (v,1), (v,2).
  These three vertices form a triangle – they are pairwise adjacent.  The
  triangle forces any independent set to contain at most one of the three
  vertices, which corresponds to choosing a colour for v.
* For each original edge {u, v} ∈ E we add edges between the same‑colour
  vertices of u and v, i.e. for each colour c ∈ {0,1,2} we add the edge
  {(u,c), (v,c)}.  This forbids assigning the same colour to the two
  adjacent vertices.

The resulting graph H has ``3 * n`` vertices.  There is an independent set
of size at least ``n`` in H iff the original graph is 3‑colourable.  The
reduction runs in O(|V| + |E|) time, i.e. polynomial time.

The module exports a single function ``reduce(instance)`` that takes a
valid ThreeColoring instance and returns a valid IndependentSet instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑Coloring instance.  It must pass
        ``ThreeColoring.validate``.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n2, "edges": edges2, "k": k}``
        such that the answer to the returned instance is *yes* exactly when
        the answer to the input instance is *yes*.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]  # number of vertices in the original graph
    original_edges: List[List[int]] = instance["edges"]

    # New graph parameters
    n2 = 3 * n  # each original vertex becomes a triangle of three vertices
    edges2: List[List[int]] = []

    # Helper to map (vertex, colour) -> new vertex index
    def idx(v: int, colour: int) -> int:
        return 3 * v + colour

    # 1. Add the triangle edges for each original vertex
    for v in range(n):
        a, b, c = idx(v, 0), idx(v, 1), idx(v, 2)
        edges2.append([a, b])
        edges2.append([a, c])
        edges2.append([b, c])

    # 2. For each original edge, add colour‑conflict edges
    for u, v in original_edges:
        for colour in range(3):
            edges2.append([idx(u, colour), idx(v, colour)])

    # The required independent‑set size is exactly n (pick one colour per
    # original vertex).
    k = n

    reduced_instance: Dict[str, Any] = {"n": n2, "edges": edges2, "k": k}
    # Validate the target instance before returning.
    IndependentSet.validate(reduced_instance)
    return reduced_instance


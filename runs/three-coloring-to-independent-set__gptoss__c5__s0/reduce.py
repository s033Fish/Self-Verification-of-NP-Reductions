"""Reduction from 3-Coloring to Independent Set.

The reduction constructs, for each vertex *v* of the original graph, three
new vertices representing the three possible colours. These three vertices
form a triangle, ensuring that an independent set can contain at most one
of them. For each original edge *(u, v)* we add edges between the colour-
copies that would give the same colour to the two endpoints – i.e. for each
colour *c* we connect the vertex representing "*u* coloured *c*" with the
vertex representing "*v* coloured *c*".  An independent set of size *n*
therefore corresponds exactly to a proper 3‑colouring of the original graph.

The function ``reduce`` validates the source instance using the provided
``ThreeColoring.validate`` method and returns a dictionary suitable for the
``IndependentSet`` problem.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` describing an
        undirected simple graph as required by :class:`ThreeColoring`.

    Returns
    -------
    dict
        An instance for :class:`IndependentSet` with keys ``"n"``,
        ``"edges"`` and ``"k"``.
    """
    # Validate the source instance – raises InvalidInstance on failure.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]

    # New graph will have 3 * n vertices.
    new_n = n * 3
    new_edges: List[List[int]] = []

    # Helper to map (vertex, colour) -> new vertex id.
    def vid(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. For each original vertex, add a triangle among its three colour
    #    vertices.
    for v in range(n):
        a, b, c = vid(v, 0), vid(v, 1), vid(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge (u, v), forbid the same colour on both
    #    endpoints by connecting the corresponding colour vertices.
    for u, v in original_edges:
        for colour in range(3):
            new_edges.append([vid(u, colour), vid(v, colour)])

    # The target asks for an independent set of size at least n (one colour
    # choice per original vertex).
    target_instance = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }

    # Validate the target instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance


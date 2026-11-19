"""Reduction from 3-Coloring to Independent Set.

Given an instance of ThreeColoring (a simple undirected graph G = (V, E)),
the reduction constructs a graph H = (V', E') and an integer k such that:

* |V'| = 3 * |V|
* k = |V|
* H has an independent set of size at least k iff G is 3‑colorable.

Construction (standard textbook reduction):
For each vertex v in G create three vertices v_0, v_1, v_2 in H
representing the three possible colours.  Connect the three vertices of the
same original vertex into a triangle – this forces an independent set to
choose at most one of them.
For each edge (u, v) in G and for each colour c ∈ {0,1,2} add an edge
between u_c and v_c.  This forbids the independent set from picking the
same colour for the two adjacent vertices.

If the original graph is 3‑colorable, picking the vertex corresponding to
the colour of each original vertex yields an independent set of size |V|.
Conversely, any independent set of size |V| must contain exactly one
vertex from each colour‑triangle, which yields a proper 3‑colouring of G.

The function ``reduce`` validates the input using the problem class
validation helpers and returns a fresh instance of IndependentSet.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, IndependentSet, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph with keys ``"n"`` and ``"edges"``.

    Returns
    -------
    dict
        An IndependentSet instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """
    # Validate the source instance first – will raise InvalidInstance on error.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]

    # New graph will have 3 * n vertices.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # Helper to map (original vertex, colour) -> new vertex index.
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add the triangle edges for each original vertex.
    for v in range(n):
        a, b, c = idx(v, 0), idx(v, 1), idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid same colour on both ends.
    for u, v in original_edges:
        for colour in range(3):
            new_edges.append([idx(u, colour), idx(v, colour)])

    # The target asks for an independent set of size at least n.
    reduced_instance: Dict[str, Any] = {"n": new_n, "edges": new_edges, "k": n}

    # Validate the target instance before returning.
    IndependentSet.validate(reduced_instance)
    return reduced_instance


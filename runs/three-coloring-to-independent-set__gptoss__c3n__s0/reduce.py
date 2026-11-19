"""Reduction from 3-Coloring to Independent Set.

The reduction follows the classic construction:

* For each vertex *v* of the original graph G we create three vertices
  ``(v, 0)``, ``(v, 1)`` and ``(v, 2)`` in the new graph H.  These three
  vertices form a clique – this forces an independent set to pick at most
  one of them, i.e. to assign at most one colour to *v*.
* For every edge ``(u, v)`` of G and for every colour ``c`` we add an edge
  between ``(u, c)`` and ``(v, c)`` in H.  This forbids the independent set
  from picking the same colour for the two adjacent vertices.

If G is 3‑colourable, we can pick for each original vertex the vertex that
represents its colour; the chosen vertices are pairwise non‑adjacent, so we
obtain an independent set of size ``n``.  Conversely, any independent set of
size ``n`` must contain exactly one of the three copies for each original
vertex, and the edges guarantee that adjacent vertices receive different
colours – yielding a proper 3‑colouring of G.

Thus the instance ``{"n": n, "edges": E}`` of ``ThreeColoring`` is mapped to
the instance ``{"n": 3*n, "edges": E', "k": n}`` of ``IndependentSet`` where
``E'`` is constructed as described above.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` describing the input
        graph for 3‑coloring.

    Returns
    -------
    dict
        A dictionary suitable for ``IndependentSet.validate`` with keys
        ``"n"``, ``"edges"`` and ``"k"``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph has 3 copies of each vertex.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # Helper to map (v, colour) -> new vertex index.
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add intra‑vertex cliques (v,0)-(v,1), (v,0)-(v,2), (v,1)-(v,2).
    for v in range(n):
        a = idx(v, 0)
        b = idx(v, 1)
        c = idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid equal colours.
    for u, v in edges:
        for colour in range(3):
            new_edges.append([idx(u, colour), idx(v, colour)])

    # The target asks for an independent set of size at least n.
    target_instance: Dict[str, Any] = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }

    # Validate the constructed target instance.
    IndependentSet.validate(target_instance)
    return target_instance


"""Reduction from 3-Coloring to Independent Set.

The reduction is the classic one used in many textbooks:

* For each vertex *v* in the original graph G we create three vertices
  ``v_0, v_1, v_2`` in the new graph H.  These three vertices form a
  triangle, guaranteeing that at most one of them can belong to an
  independent set.
* For each edge ``(u, v)`` in G and for each colour ``c`` (0,1,2) we add
  an edge between ``u_c`` and ``v_c``.  This forbids two adjacent vertices
  in G from taking the same colour.

An independent set of size *n* in H therefore selects exactly one of the
three copies for each original vertex, and the edges ensure that the
selected copies correspond to a proper 3‑colouring of G.  Conversely, a
proper 3‑colouring of G yields an independent set of size *n* by picking
the appropriate copy for each vertex.

The function ``reduce`` takes a valid instance of ``ThreeColoring`` and
produces a valid instance of ``IndependentSet`` with ``k = n``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` describing the
        original graph.  The instance is assumed to be valid according to
        :class:`ThreeColoring.validate`.

    Returns
    -------
    dict
        An instance of :class:`IndependentSet` with ``n' = 3 * n``, the
        constructed edge list and ``k = n``.
    """
    # Validate the source instance – this will raise ``InvalidInstance``
    # if the format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have 3 copies per vertex.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add the triangle edges for each original vertex.
    for v in range(n):
        base = 3 * v
        # edges: (base, base+1), (base, base+2), (base+1, base+2)
        new_edges.append([base, base + 1])
        new_edges.append([base, base + 2])
        new_edges.append([base + 1, base + 2])

    # 2. For each original edge, connect same‑colour copies.
    for u, v in edges:
        for colour in range(3):
            new_u = 3 * u + colour
            new_v = 3 * v + colour
            new_edges.append([new_u, new_v])

    # Assemble the target instance.
    target_instance: Dict = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }

    # Validate the produced instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance


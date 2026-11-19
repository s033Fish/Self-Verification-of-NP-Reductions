"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` (graph 3‑colorability).
The target problem is :class:`IndependentSet`.

For a given graph G = (V, E) we construct a graph H = (V', E') and an
integer k such that:

* ``k = |V|`` – we ask for an independent set of size exactly the number of
  original vertices.
* For each vertex ``v`` in ``V`` we create three vertices ``(v, 0)``,
  ``(v, 1)`` and ``(v, 2)`` in ``V'``.  These represent the three possible
  colours.
* To enforce that at most one colour is chosen for each original vertex we
  add a triangle among the three copies of ``v`` – i.e. edges between every
  pair of the three vertices.
* To enforce proper colouring of adjacent vertices we add, for every edge
  ``{u, v}`` in ``E`` and for each colour ``c`` in ``{0,1,2}``, an edge
  between ``(u, c)`` and ``(v, c)``.  This forbids both endpoints of an edge
  from taking the same colour.

The resulting graph H has ``3 * |V|`` vertices.  An independent set of size
``|V|`` in H corresponds exactly to a proper 3‑colouring of G: the set must
contain exactly one vertex from each triangle (otherwise it would have at
most ``|V|-1`` vertices), and the colour‑conflict edges guarantee that adjacent
original vertices receive different colours.

Conversely, a proper 3‑colouring of G yields an independent set of size
``|V|`` in H by selecting the vertex representing the colour of each original
vertex.

Thus the reduction is correct and runs in polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ``ThreeColoring`` instance.  It must
        contain the keys ``"n"`` and ``"edges"`` as described in the
        problem statement.

    Returns
    -------
    dict
        A dictionary representing an ``IndependentSet`` instance with keys
        ``"n"``, ``"edges"`` and ``"k"``.
    """

    # Validate the source instance – will raise InvalidInstance if malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have 3*n vertices. Vertex ids: 3*v + colour.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add triangle edges for each original vertex.
    for v in range(n):
        base = 3 * v
        new_edges.append([base + 0, base + 1])
        new_edges.append([base + 0, base + 2])
        new_edges.append([base + 1, base + 2])

    # 2. Add conflict edges for each original edge.
    for u, v in edges:
        for colour in range(3):
            new_u = 3 * u + colour
            new_v = 3 * v + colour
            new_edges.append([new_u, new_v])

    target_instance = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }

    # Validate the produced target instance.
    IndependentSet.validate(target_instance)
    return target_instance


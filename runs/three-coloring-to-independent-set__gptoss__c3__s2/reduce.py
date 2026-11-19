"""Reduction from 3-Coloring to Independent Set.

The reduction is classic: replace each vertex *v* of the original graph by a
triangle of three vertices representing the three possible colours.  Edges are
added so that at most one vertex of each triangle can appear in an independent
set (the triangle edges) and so that adjacent vertices in the original graph
cannot be assigned the same colour (edges between corresponding colour nodes).

An independent set of size *n* (where *n* is the number of original vertices)
corresponds exactly to a proper 3‑colouring of the original graph.  Therefore
the instance ``{"n": n, "edges": E}`` of ``ThreeColoring`` is transformed into
an ``IndependentSet`` instance with ``k = n``.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes defined in problems.py
from problems import SOURCE, TARGET, ThreeColoring, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A valid instance of ``ThreeColoring`` – it must contain the keys
        ``"n"`` and ``"edges"`` as described in the problem statement.

    Returns
    -------
    dict
        A valid ``IndependentSet`` instance ``{"n": 3*n, "edges": ..., "k": n}``
        such that the original instance is a *yes* instance iff the returned
        instance is a *yes* instance.
    """

    # Validate the source instance first – this will raise InvalidInstance if
    # the format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have three vertices for each original vertex.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add a triangle for each original vertex so that at most one colour
    #    vertex can be chosen.
    for v in range(n):
        a = 3 * v
        b = a + 1
        c = a + 2
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge (u, v) and each colour c, forbid both ends
    #    from taking the same colour by connecting the corresponding colour
    #    vertices.
    for u, v in edges:
        for colour in range(3):
            a = 3 * u + colour
            b = 3 * v + colour
            new_edges.append([a, b])

    # The required independent set size is exactly the number of original
    # vertices.
    k = n

    reduced_instance = {"n": new_n, "edges": new_edges, "k": k}

    # Ensure the produced instance conforms to the TARGET specification.
    IndependentSet.validate(reduced_instance)
    return reduced_instance


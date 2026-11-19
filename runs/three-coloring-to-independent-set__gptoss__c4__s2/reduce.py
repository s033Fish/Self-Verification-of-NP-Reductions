"""Reduction from 3-Coloring to Independent Set.

The reduction is the classic one used in textbooks:

* For each vertex *v* of the original graph we create three vertices
  ``v_0, v_1, v_2`` representing the three possible colours.
* The three vertices belonging to the same original vertex form a triangle
  (pairwise edges).  This forces any independent set to contain **at most**
  one of them – the independent set will therefore choose at most one colour
  for each original vertex.
* For each original edge ``(u, v)`` we add edges between the *same colour*
  vertices of the two endpoints: ``u_i`` is adjacent to ``v_i`` for each
  colour ``i``.  This prevents the independent set from picking the same
  colour for two adjacent vertices.

With this construction, an independent set of size ``n`` (where ``n`` is the
number of vertices of the original graph) corresponds exactly to a proper
3‑colouring of the original graph, and vice‑versa.

The reduction runs in polynomial time – the output graph has ``3·n``
vertices and at most ``3·n`` (triangle edges) + ``3·|E|`` (cross edges) edges.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ThreeColoring instance. It must pass
        ``ThreeColoring.validate``.

    Returns
    -------
    dict
        An IndependentSet instance ``{"n": n', "edges": [...], "k": k}``
        where ``n' = 3 * n`` and ``k = n``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have 3*n vertices, indexed as follows:
    #   vertex (original) v, colour c (0,1,2)  ->  new_id = 3*v + c
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add the triangle edges for each original vertex.
    for v in range(n):
        base = 3 * v
        # edges between (base, base+1), (base, base+2), (base+1, base+2)
        new_edges.append([base, base + 1])
        new_edges.append([base, base + 2])
        new_edges.append([base + 1, base + 2])

    # 2. For each original edge (u, v), connect same‑colour vertices.
    for u, v in edges:
        for colour in range(3):
            new_u = 3 * u + colour
            new_v = 3 * v + colour
            new_edges.append([new_u, new_v])

    # The target asks for a *minimum* independent set size k, we set k = n.
    target_instance = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }

    # Validate the constructed target instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance


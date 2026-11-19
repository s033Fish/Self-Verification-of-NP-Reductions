"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` (graph 3‑colorability) and the
target problem is :class:`IndependentSet` (existence of an independent set of
size *k*).  For an input graph ``G = (V, E)`` we construct a new graph ``G'``
as follows (the classic textbook reduction):

* For each vertex ``v`` in ``V`` create three vertices ``(v, 0)``, ``(v, 1)``
  and ``(v, 2)``.  Connect them into a triangle – this forces any independent
  set to pick *at most* one of the three, modelling the choice of a colour.
* For each original edge ``{u, v}`` and for each colour ``c`` add an edge
  between ``(u, c)`` and ``(v, c)``.  This forbids two adjacent vertices from
  receiving the same colour.

The resulting graph has ``3 * |V|`` vertices.  There is an independent set of
size ``|V|`` in ``G'`` iff the original graph is 3‑colourable: pick exactly one
vertex from each triangle according to a proper colouring.

The reduction runs in polynomial time (linear in the size of the input) and
produces a valid ``IndependentSet`` instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for type checking / documentation.  The
# reduction itself does not need to call any methods of the classes.
from problems import SOURCE, TARGET  # noqa: F401  (imported for side‑effects only)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Map a ``ThreeColoring`` instance to an ``IndependentSet`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs) describing the input graph.

    Returns
    -------
    dict
        An ``IndependentSet`` instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.  The graph has ``3 * n`` vertices, the edge set encodes the
        construction described above, and ``k = n``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have 3 * n vertices.
    new_n = 3 * n
    edge_set = set()

    # 1. Add the triangle edges for each original vertex.
    for v in range(n):
        a = 3 * v
        b = a + 1
        c = a + 2
        # Undirected edges are stored as frozenset of the two endpoints.
        edge_set.add(frozenset((a, b)))
        edge_set.add(frozenset((a, c)))
        edge_set.add(frozenset((b, c)))

    # 2. For each original edge, connect same‑colour vertices.
    for u, v in edges:
        for colour in range(3):
            a = 3 * u + colour
            b = 3 * v + colour
            edge_set.add(frozenset((a, b)))

    # Convert the set of frozensets back to the required list-of-lists format.
    new_edges = [list(e) for e in edge_set]

    # The target asks for an independent set of size at least n.
    k = n

    return {"n": new_n, "edges": new_edges, "k": k}


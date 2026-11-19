"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`SetCover` defined in the same file.

For a graph G = (V, E) we construct a set‑cover instance where:

* The universe consists of one element for each edge of G.
* For each vertex v ∈ V we create a set containing exactly those universe
  elements (edges) that are incident to v.
* The budget ``k`` is unchanged.

It is well‑known that G has a vertex cover of size at most k iff the
constructed set‑cover instance has a cover of size at most k.

The implementation below follows this construction while respecting the
validation rules defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import VertexCover, SetCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the VertexCover specification.

    Returns
    -------
    dict
        A dictionary that conforms to the SetCover specification.

    The reduction runs in time linear in the size of the graph (``O(|V|+|E|)``).
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Map each edge to a unique universe element (its index).
    # The order of edges in the list is already a suitable indexing.
    edge_index: Dict[tuple[int, int], int] = {}
    for idx, (u, v) in enumerate(edges):
        # Store both (u, v) and (v, u) for easy lookup later.
        edge_index[(u, v)] = idx
        edge_index[(v, u)] = idx

    # Build the list of sets – one per vertex.
    sets: List[List[int]] = []
    for v in range(n):
        incident: List[int] = []
        for (u, w) in edges:
            # If v is an endpoint of the edge, include its index.
            if v == u or v == w:
                incident.append(edge_index[(u, w)])
        # The SetCover validator requires each set to have distinct elements,
        # which is already true because edge indices are unique.
        sets.append(incident)

    # Construct the target instance.
    target_instance: Dict[str, Any] = {
        "universe_size": len(edges),
        "sets": sets,
        "k": k,
    }

    # Validate the produced instance to catch programming errors early.
    SetCover.validate(target_instance)
    return target_instance


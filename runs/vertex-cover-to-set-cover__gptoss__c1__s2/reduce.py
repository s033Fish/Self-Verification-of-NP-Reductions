"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) instance format is::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered 0..n-1 and ``edges`` is a list of unordered
pairs.  The task is to decide whether there exists a set of at most ``k``
vertices that touches every edge.

The target problem (SetCover) instance format is::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0..u-1`` and each set is a
list of distinct universe elements.

The classic polynomial‑time reduction maps each edge to a distinct element
of the universe and each vertex to a set containing exactly the edges
incident to that vertex.  Selecting at most ``k`` vertices that cover all
edges corresponds exactly to selecting at most ``k`` of the constructed
sets that cover the whole universe.

The reduction handles all edge cases automatically because the
construction preserves the semantics of ``k`` (negative ``k`` stays
negative, an empty edge list yields an empty universe, etc.).
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        specification of VertexCover.

    Returns
    -------
    dict
        A SetCover instance ``{"universe_size": u, "sets": [...], "k": k}``
        that is a yes‑instance iff the original VertexCover instance is a
        yes‑instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Number of edges defines the size of the universe.
    m: int = len(edges)

    # Build, for each vertex, the list of incident edge indices.
    # ``sets[v]`` will contain the indices of edges that have ``v`` as an
    # endpoint.  Edge indices serve as the universe elements.
    sets: List[List[int]] = []
    for v in range(n):
        incident: List[int] = []
        for idx, (u, w) in enumerate(edges):
            if u == v or w == v:
                incident.append(idx)
        sets.append(incident)

    return {"universe_size": m, "sets": sets, "k": k}


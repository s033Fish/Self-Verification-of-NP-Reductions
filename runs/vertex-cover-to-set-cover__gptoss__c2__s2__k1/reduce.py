"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0..n-1`` and ``edges`` is a list of undirected
edges (each edge appears at most once).  The question is whether there exists a
set of at most ``k`` vertices that touches every edge.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0..u-1`` and each entry in
``sets`` is a list of distinct elements.

The classic polynomial‑time reduction maps each edge to a distinct element of
the universe and each vertex to the set of edges incident to that vertex.  A
vertex cover of size ``k`` corresponds exactly to a set cover of size ``k``
that covers all edge‑elements, and vice‑versa.

The ``reduce`` function below implements this transformation.  It runs in
``O(n + m)`` time where ``m`` is the number of edges, which is polynomial in the
size of the input instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance with keys ``"n"``,
        ``"edges"`` and ``"k"`` as described in the problem statement.

    Returns
    -------
    dict
        A SetCover instance with keys ``"universe_size"``, ``"sets"`` and
        ``"k"``.  The answer to the returned instance is *yes* iff the answer
        to the input instance is *yes*.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Each edge becomes a unique element of the universe.
    m = len(edges)
    # Build a list of sets for each vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]

    for idx, (u, v) in enumerate(edges):
        # Add the edge index to the set of both incident vertices.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets; the order of sets does not
    # matter, but we preserve the natural vertex ordering.
    set_cover_instance: Dict[str, Any] = {
        "universe_size": m,
        "sets": vertex_sets,
        "k": k,
    }
    return set_cover_instance

# The module may be imported by an external harness that expects a ``reduce``
# callable.  No top‑level test code is executed here.

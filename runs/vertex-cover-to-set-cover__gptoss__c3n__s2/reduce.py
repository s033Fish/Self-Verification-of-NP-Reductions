"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`SetCover` defined in the same module.

Given a graph G = (V, E) and an integer k, we construct a set‑cover
instance where the universe consists of the edges of G (each edge is
identified by its index in the ``edges`` list) and for each vertex v we
create a set containing exactly those edge indices incident to v.

Formally:
    universe_size = |E|
    sets[v] = { i | edge i = [u, w] and (u == v or w == v) }
    k' = k

It is easy to see that a collection of at most k vertices covers all
edges iff the corresponding collection of at most k sets covers the
entire universe.  The construction is clearly polynomial‑time.

The ``reduce`` function validates the input using the source class and
returns a dictionary that conforms to the target format.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import VertexCover, SetCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance. It must contain
        the keys ``"n"``, ``"edges"`` and ``"k"`` as described in the
        problem statement.

    Returns
    -------
    dict
        A SetCover instance with keys ``"universe_size"``, ``"sets"`` and
        ``"k"``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is incorrect.
    VertexCover.validate(instance)

    n: int = instance["n"]          # number of vertices (0..n-1)
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe: each edge gets a unique index.
    m = len(edges)
    # Build for each vertex the list of incident edge indices.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets (order does not matter).
    # We include a set for every vertex, even if it is empty (possible when a
    # vertex is isolated). Empty sets are allowed by the target definition.
    sets: List[List[int]] = vertex_sets

    return {
        "universe_size": m,
        "sets": sets,
        "k": k,
    }


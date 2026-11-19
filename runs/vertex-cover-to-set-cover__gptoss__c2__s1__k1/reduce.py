"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0`` through ``n-1`` and ``edges`` is a list of
undirected edges (each edge appears only once).  The decision question is
whether there exists a vertex cover of size **at most** ``k``.

The target problem (SetCover) expects instances of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0`` … ``u-1`` and ``sets`` is a
list of subsets of that universe.  The decision question is whether a
selection of at most ``k`` of those subsets covers the entire universe.

The classical polynomial‑time reduction maps each edge of the graph to a
distinct element of the universe and creates, for every vertex ``v``, a set
containing exactly those edge‑elements incident to ``v``.  Selecting a vertex
corresponds to selecting its incident‑edge set, and covering all edges is
equivalent to covering the whole universe.

The implementation below follows that construction directly.  It runs in
``O(n + |E|)`` time, which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance with keys ``n``,
        ``edges`` and ``k`` as described in the module docstring.

    Returns
    -------
    dict
        A SetCover instance ``{"universe_size": u, "sets": [...], "k": k}``
        such that the SetCover instance is a *yes* instance iff the original
        VertexCover instance is a *yes* instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Map each edge to a unique element index in the universe.
    # The universe size is simply the number of edges.
    universe_size = len(edges)

    # Build a list of sets, one per vertex. Each set contains the indices of
    # edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        # Add the edge index to both endpoint vertices' sets.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover format does not require any particular ordering of the
    # sets, but we keep the natural vertex order for clarity.
    result: Dict[str, Any] = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }
    return result


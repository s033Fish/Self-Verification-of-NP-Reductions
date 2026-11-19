"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0..n-1`` and ``edges`` is a list of unordered
pairs.  The question is whether there exists a vertex cover of size at most
``k``.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0..u-1`` and each entry in
``sets`` is a list of distinct universe elements.  The question is whether a
selection of at most ``k`` of those sets covers the entire universe.

The classic polynomial‑time reduction maps each edge of the graph to a unique
universe element and creates one set for each vertex containing exactly the
edges incident to that vertex.  Selecting a collection of at most ``k`` sets
that covers all edges corresponds precisely to selecting at most ``k``
vertices that touch every edge – i.e., a vertex cover.

The implementation below follows this construction.  It handles all edge
cases automatically: isolated vertices yield empty sets (allowed by the
SetCover definition), an empty edge list produces a universe of size ``0``
which is trivially covered, and the parameter ``k`` is passed through unchanged.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        specification of the VertexCover problem.

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

    # Assign a unique index to each edge to serve as universe elements.
    # The order of edges in the input list is already suitable.
    edge_index = {tuple(e): idx for idx, e in enumerate(edges)}
    # In case edges are given as [v, u] where u<v, we also map the reversed
    # tuple to the same index because the graph is undirected.
    for idx, e in enumerate(edges):
        u, v = e
        edge_index[(v, u)] = idx

    universe_size = len(edges)

    # Build a set for each vertex containing the indices of incident edges.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover format allows duplicate sets and empty sets, so we can
    # directly use ``vertex_sets``.
    sets = vertex_sets

    return {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }


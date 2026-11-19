"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled ``0`` … ``n-1``), ``edges``
is a list of undirected edges (each a two‑element list) and ``k`` is the
budget for the vertex cover.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0`` … ``u-1`` and each set
contains distinct elements of that universe.

The classic polynomial‑time reduction maps each edge of the graph to a
distinct element of the universe and creates, for every vertex ``v``, a
set containing exactly the elements (edges) incident to ``v``.  A set of
vertices of size at most ``k`` covers all edges iff the corresponding
sets of size at most ``k`` cover the entire universe.

The implementation below follows this construction directly.  It runs
in time linear in the size of the input graph, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Set Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as
        described in the problem statement.

    Returns
    -------
    dict
        A Set Cover instance with keys ``"universe_size"``, ``"sets"``
        and ``"k"``.
    """

    # Extract the components of the Vertex Cover instance.
    n: int = int(instance.get("n", 0))
    edges: List[List[int]] = list(instance.get("edges", []))
    k: int = int(instance.get("k", 0))

    # The universe consists of one element per edge.
    m: int = len(edges)
    universe_size = m

    # Build the sets: one set per vertex containing indices of incident edges.
    sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        # Add this edge index to the sets of its two endpoints.
        sets[u].append(idx)
        sets[v].append(idx)

    # The reduction preserves the budget ``k``.
    return {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }


__all__ = ["reduce"]

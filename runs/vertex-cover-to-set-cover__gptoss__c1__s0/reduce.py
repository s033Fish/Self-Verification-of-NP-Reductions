"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0..n-1`` and ``edges`` is a list of
undirected edges.  The decision question is whether there exists a set of
at most ``k`` vertices that touches every edge.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0..u-1`` and each set lists
the elements it contains.  The decision question is whether at most ``k``
sets cover the entire universe.

The classic polynomial‑time reduction creates one element of the universe
for each edge and one set for each vertex containing exactly the elements
corresponding to the edges incident to that vertex.  A vertex cover of size
``k`` corresponds directly to a set cover of size ``k`` and vice‑versa.

The ``reduce`` function below implements this transformation.  It runs in
time linear in the size of the input graph (i.e., ``O(n + |E|)``), which is
polynomial.  Edge‑case handling is implicit: if ``k < 0`` the answer is
always ``no`` for both problems, and if there are no edges the universe
size is ``0`` making the Set‑Cover instance trivially a ``yes`` for any
``k >= 0`` – exactly matching the Vertex‑Cover semantics.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Set Cover instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[List[int]], "k": int}``

    Returns
    -------
    dict
        ``{"universe_size": int, "sets": List[List[int]], "k": int}``
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])
    k: int = instance.get("k", 0)

    # Assign a unique index to each edge – this will be the element in the
    # Set‑Cover universe.
    # The order of edges does not matter; we simply enumerate them.
    edge_index = {tuple(e): idx for idx, e in enumerate(edges)}
    universe_size = len(edges)

    # Initialise a set list for each vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]

    for u, v in edges:
        idx = edge_index[(u, v)] if (u, v) in edge_index else edge_index[(v, u)]
        # Add this edge index to the incident vertices' sets.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover format allows duplicate sets and empty sets, which is fine.
    # We simply return the list of vertex sets.
    return {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }


__all__ = ["reduce"]

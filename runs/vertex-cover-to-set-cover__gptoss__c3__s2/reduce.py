"""Reduction from Vertex Cover to Set Cover.

The source problem is ``VertexCover`` (defined in *problems.py*) with
instance format ``{"n": n, "edges": [[u, v], ...], "k": k}``.
The target problem is ``SetCover`` with format ``{"universe_size": u,
"sets": [[element, ...], ...], "k": k}``.

For each vertex we create a set that contains the *indices* of all edges
incident to that vertex.  The universe consists of one element for each
edge.  A collection of vertices covers all edges iff the corresponding
collection of sets covers the entire universe.  The parameter ``k`` is
preserved.

The reduction runs in time linear in the size of the graph, which is
polynomial in the input length.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Set Cover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the VertexCover specification.

    Returns
    -------
    dict
        A dictionary adhering to the SetCover specification such that
        ``VertexCover.is_yes(instance)`` equals ``SetCover.is_yes(reduced)``.
    """
    # Extract fields – we rely on the caller to have provided a valid
    # VertexCover instance (the benchmark harness validates before calling
    # the reduction).  No heavy validation is performed here to keep the
    # function fast.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Assign each edge a unique index to serve as an element of the universe.
    # The order does not matter; we simply enumerate the list.
    edge_index = {tuple(e): idx for idx, e in enumerate(edges)}
    universe_size = len(edges)

    # For each vertex build the list of incident edge indices.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets (order does not matter).
    # Vertices with no incident edges will correspond to empty sets – this is
    # allowed by the SetCover definition.
    return {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }


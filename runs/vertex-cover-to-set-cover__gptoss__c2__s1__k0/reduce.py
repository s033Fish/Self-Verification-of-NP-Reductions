"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled 0 .. n-1), ``edges`` is a
list of undirected edges (each edge appears at most once) and ``k`` is the
size bound for the vertex cover.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where ``u`` is the size of the universe (elements are 0 .. u-1), ``sets`` is
 a list of subsets of the universe and ``k`` is the bound on the number of
 sets that may be chosen.

The classic polynomial‑time reduction maps each edge of the graph to a
distinct element of the universe and creates, for every vertex, a set that
contains exactly the elements (edges) incident to that vertex.  Selecting a
set corresponds to picking the associated vertex for the cover.  An edge is
covered in the vertex‑cover instance iff at least one of its two incident
vertices is selected, which is exactly the condition that the corresponding
universe element is covered by at least one chosen set.

The reduction therefore preserves the answer: the graph has a vertex cover
of size ≤ k iff the constructed set‑cover instance has a set cover of size
≤ k.

The implementation below follows this construction and runs in time linear
in the size of the input (``O(n + |E|)``), which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SetCover instance with keys ``"universe_size"``, ``"sets"`` and
        ``"k"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Map each edge to a unique index to serve as an element of the universe.
    # The order of edges in the list already provides a natural indexing.
    m = len(edges)  # number of edges = universe size

    # Initialize a list of sets for each vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]

    for idx, (u, v) in enumerate(edges):
        # Add the edge index to the sets of both incident vertices.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance.
    return {
        "universe_size": m,
        "sets": vertex_sets,
        "k": k,
    }


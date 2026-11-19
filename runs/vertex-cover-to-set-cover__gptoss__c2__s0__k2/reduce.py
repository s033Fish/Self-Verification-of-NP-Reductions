"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) instance format is a dictionary:

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered 0..n-1 and ``edges`` is a list of unordered
pairs.  The task is to decide whether there exists a vertex cover of size
at most ``k``.

The target problem (SetCover) instance format is a dictionary:

    {"universe_size": u, "sets": [[e1, e2, ...], ...], "k": k}

where the universe consists of the elements 0..u-1.  The question is
whether at most ``k`` of the given sets together contain every element of
the universe.

Standard polynomial‑time reduction:

* Treat each edge of the graph as a distinct element of the universe.
* For each vertex ``v`` create a set that contains exactly those edge‑indices
  incident to ``v``.
* Keep the same ``k``.

Correctness:
    - If a set of vertices ``C`` covers all edges, then the corresponding
      sets for those vertices cover the entire universe, giving a set cover
      of size |C| ≤ k.
    - Conversely, any set cover of size ≤ k must consist of sets that are
      associated with vertices; taking those vertices yields a vertex cover
      of the same size.

Edge cases are handled automatically:
    * ``k < 0`` remains a no‑instance for both problems.
    * An empty edge list yields ``universe_size = 0``; any ``k ≥ 0`` is a
      yes‑instance for SetCover, matching the VertexCover semantics.
    * Vertices with no incident edges produce empty sets, which is allowed
      by the SetCover definition.

The reduction runs in time O(n + m) where ``m`` is the number of edges.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a VertexCover instance into an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SetCover instance dictionary with keys ``"universe_size"``,
        ``"sets"`` and ``"k"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The universe consists of one element per edge.
    universe_size = len(edges)

    # Prepare a list of sets, one per vertex.
    # Each set will contain the indices of edges incident to that vertex.
    sets: List[List[int]] = [[] for _ in range(n)]

    for idx, (u, v) in enumerate(edges):
        # Add this edge index to the sets for both incident vertices.
        sets[u].append(idx)
        sets[v].append(idx)

    # The SetCover format expects a list of sets (each a list of elements).
    # Empty sets are allowed, and duplicate sets are also allowed, but we
    # simply output one set per vertex.
    return {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }


"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled ``0`` through ``n-1``),
``edges`` is a list of undirected edges (each a two‑element list) and ``k``
is the size bound.

The target problem (SetCover) expects an instance of the form::

    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

where the universe consists of the elements ``0`` … ``u-1`` and each set
lists distinct elements of that universe.

The classic polynomial‑time reduction maps each vertex to the set of edges it
covers.  The universe is the set of edges (identified by their index in the
``edges`` list).  Formally, for each vertex ``v`` we create a set ``S_v`` that
contains the index ``i`` of every edge ``edges[i]`` incident to ``v``.

Correctness sketch:
    * If there is a vertex cover of size ≤ k, picking the corresponding sets
      yields a set cover of size ≤ k because every edge has at least one
      endpoint in the cover and therefore appears in at least one chosen set.
    * Conversely, a set cover of size ≤ k selects ≤ k vertex‑sets whose union
      contains all edge indices, meaning each edge is incident to at least
      one selected vertex, i.e., those vertices form a vertex cover.

Edge‑case handling matches the specifications of both problems without any
additional work:
    * ``k < 0`` maps to a set‑cover instance with the same ``k`` – both are
      automatically unsatisfiable.
    * An empty edge list yields ``universe_size = 0`` and ``n`` empty sets;
      the SetCover definition declares this a yes‑instance for any ``k ≥ 0``.

The implementation runs in ``O(n + m)`` time, where ``m`` is the number of
edges, which is polynomial in the input size.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the VertexCover format described above.

    Returns
    -------
    dict
        A dictionary representing the equivalent SetCover instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The universe consists of the edges themselves, identified by their index.
    m = len(edges)
    universe_size = m

    # Build a list of sets, one per vertex. Each set contains the indices of
    # edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        # Since the input guarantees u != v and vertices are within range, we
        # can safely add the edge index to both endpoint sets.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets. The order of sets is not
    # important, but we keep the natural vertex order for clarity.
    sets = vertex_sets

    return {"universe_size": universe_size, "sets": sets, "k": k}


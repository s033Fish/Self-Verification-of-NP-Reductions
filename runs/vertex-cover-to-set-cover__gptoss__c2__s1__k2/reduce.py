"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) instance format is:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1 and edges are undirected pairs.

The target problem (SetCover) instance format is:
    {"universe_size": u, "sets": [[element, ...], ...], "k": k}
where the universe consists of elements 0..u-1.

Reduction construction:
    * Each edge of the graph becomes a distinct element of the universe.
    * For every vertex v we create a set containing exactly those edge‑indices
      that are incident to v.
    * The budget k is kept unchanged.

Correctness sketch:
    * Selecting a vertex cover of size ≤ k corresponds to selecting the same
      vertices (i.e., their incident‑edge sets) which together contain every
      edge element – a set cover of size ≤ k.
    * Conversely, any set cover of size ≤ k must consist of sets that are the
      incident‑edge sets of some vertices, and those vertices cover all edges.
    * Edge cases (k < 0, empty edge list, k ≥ n) are preserved because the
      construction mirrors the original instance semantics.

The reduction runs in time linear in the size of the graph, which is
polynomial.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Vertex Cover instance to an equivalent Set Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``n`` (int), ``edges`` (list of [u, v]), and
        ``k`` (int) following the VertexCover specification.

    Returns
    -------
    dict
        A SetCover instance dictionary with keys ``universe_size``, ``sets``
        and ``k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Map each edge to a unique element index.
    # The universe size is the number of edges.
    m = len(edges)
    universe_size = m

    # Prepare a list of sets for each vertex.
    # Using list of lists to match the expected format (distinct elements).
    vertex_sets: List[List[int]] = [[] for _ in range(n)]

    for idx, (u, v) in enumerate(edges):
        # Add this edge index to the incident vertex sets.
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets (order does not matter).
    # We include a set for every vertex, even if it is empty (which is allowed).
    sets = vertex_sets

    return {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }


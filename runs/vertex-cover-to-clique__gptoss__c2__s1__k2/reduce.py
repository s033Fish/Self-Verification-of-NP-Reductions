"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) expects an instance dictionary:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (Clique) expects the same format, but the meaning of
"k" is different.  We construct the complement graph G' of the input
graph G and set k' = n - k.  It is well‑known that G has a vertex cover of
size at most k iff G' has a clique of size at least n - k.

The reduction runs in O(n^2) time, which is polynomial in the size of the
input instance.
"""

from typing import List, Dict, Any


def _edge_key(u: int, v: int) -> tuple:
    """Return a canonical representation of an undirected edge.

    The input instances guarantee that ``u != v`` and that each edge appears
    only once (either [u, v] or [v, u]).  By sorting the pair we obtain a
    unique key that can be stored in a set for O(1) look‑ups.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent Clique instance.

    Parameters
    ----------
    instance: dict
        A Vertex Cover instance with keys ``n``, ``edges`` and ``k``.

    Returns
    -------
    dict
        A Clique instance that is a yes‑instance exactly when the original
        Vertex Cover instance is a yes‑instance.
    """
    n: int = instance["n"]
    k: int = instance["k"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Build a set of edges for fast membership testing.
    edge_set = set(_edge_key(u, v) for u, v in original_edges)

    # Complement graph edges: every unordered pair not present in the
    # original edge set becomes an edge.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in edge_set:
                complement_edges.append([u, v])

    # The new k for the Clique problem is n - k (size of the independent set
    # we are looking for in the original graph).
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}


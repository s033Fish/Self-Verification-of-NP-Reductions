"""Reduction from Clique to Vertex Cover.

The source problem is **Clique** with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
where the graph has vertices 0..n-1 and we ask whether there exists a clique
of size **at least** ``k``.

The target problem is **VertexCover** with the same graph representation and
asks whether there exists a vertex cover of size **at most** ``k``.

Standard polynomial‑time reduction:
    • Take the complement graph \bar{G} of the input graph G.
    • Set ``k' = n - k``.

Reasoning:
    A set of vertices forms a clique of size k in G iff the remaining
    vertices (n‑k of them) form a vertex cover of \bar{G}.  This equivalence
    respects all edge cases described in the problem statements:
        - k <= 0  →  k' >= n  →  VertexCover is trivially yes.
        - k = 1   →  k' = n-1 →  any graph has a vertex cover of size n-1.
        - k > n   →  k' < 0   →  VertexCover is trivially no.

The reduction runs in O(n^2) time, which is polynomial in the size of the
input instance.
"""

from typing import List, Dict, Any


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected simple graph.

    Parameters
    ----------
    n: int
        Number of vertices (0 .. n-1).
    edges: List[List[int]]
        List of edges of the original graph. Each edge is a two‑element list
        ``[u, v]`` with ``u != v`` and ``0 <= u, v < n``.

    Returns
    -------
    List[List[int]]
        Edge list of the complement graph, using the same representation.
    """
    # Store original edges in a set of ordered tuples for O(1) look‑ups.
    original = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        original.add((u, v))

    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A Clique instance with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        A VertexCover instance preserving the yes/no answer.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Vertex cover size parameter.
    k_prime = n - k

    return {"n": n, "edges": comp_edges, "k": k_prime}


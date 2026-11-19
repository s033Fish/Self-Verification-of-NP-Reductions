"""Reduction from Clique to Vertex Cover.

The source problem (Clique) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (VertexCover) instance format is identical except that the
interpretation of ``k`` is different.  A Clique of size at least ``k`` exists in
the original graph *G* iff a Vertex Cover of size at most ``n - k`` exists in
the complement graph ``G̅``.

The reduction therefore constructs the complement graph (same vertex set, all
non‑edges become edges) and maps ``k`` to ``n - k``.

This transformation respects all edge cases described in the problem
definitions:
* ``k <= 0`` → ``n - k >= n`` → VertexCover instance is trivially yes.
* ``k > n`` → ``n - k < 0`` → VertexCover instance is trivially no.
* ``k = 1`` → ``n - 1`` → any graph has a vertex cover of size ``n-1``.

The function runs in O(n^2) time, which is polynomial in the size of the
input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``n``, ``edges`` and ``k`` representing the
        Clique problem.

    Returns
    -------
    dict
        A dictionary representing the equivalent VertexCover instance.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Build a set of existing edges for O(1) look‑up. Store as ordered tuples.
    edge_set = {tuple(sorted(e)) for e in original_edges}

    # Complement edges: all unordered pairs (i, j) with i < j that are not in
    # the original edge set.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # The vertex‑cover parameter is n - k.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}


"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (Clique) instance format is identical, but the meaning
of ``k`` is different.  The reduction constructs the complement graph of the
input graph and transforms the size bound ``k`` accordingly.

Correctness sketch:
    Let G = (V, E) be the input graph and let k be the vertex‑cover bound.
    Set k' = n - k.  In the complement graph G̅ the edge set consists of all
    non‑edges of G.  A set S ⊆ V is a vertex cover of size ≤ k in G iff the
    complement V \ S is an independent set of size ≥ n - k in G.  An
    independent set in G corresponds exactly to a clique in the complement
    graph G̅.  Hence G has a vertex cover of size ≤ k iff G̅ has a clique of
    size ≥ k'.

Edge‑case handling follows automatically from the transformation:
    * k < 0 ⇒ k' > n, and the Clique definition says k > n is a NO instance.
    * k ≥ n ⇒ k' ≤ 0, and the Clique definition says k ≤ 0 is a YES instance.

The implementation runs in O(n²) time, which is polynomial in the size of
the input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Vertex Cover instance as described in ``problems.py``.

    Returns
    -------
    dict
        A Clique instance that is a yes‑instance iff the original Vertex
        Cover instance is a yes‑instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set of undirected edges for O(1) lookup. Store each edge with
    # the smaller vertex first.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Complement edges: all pairs (i, j) with i < j that are not in edge_set.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # Transform the size bound.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}


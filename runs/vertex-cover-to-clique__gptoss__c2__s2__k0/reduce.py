"""Reduction from Vertex Cover to Clique.

The source problem is *Vertex Cover* with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is *Clique* with the same instance format.  The classic
polynomial‑time reduction uses the complement graph:

    G has a vertex cover of size ≤ k  ⇔  the complement of G has a clique of
    size ≥ n − k.

Therefore we construct the complement of the input graph and set the new
parameter ``k_target = n - k``.  This mapping correctly handles all edge
cases described in the problem statements (e.g., ``k < 0`` or ``k ≥ n``).

The function ``reduce`` takes a source instance dictionary and returns a
target instance dictionary.  It runs in O(n²) time, which is polynomial in the
size of the input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A vertex‑cover instance with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        A clique instance where ``k_target = n - k`` and the edge list
        corresponds to the complement of the original graph.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set of existing edges for O(1) membership tests.  Store each
    # undirected edge as a tuple (min, max) to avoid duplication.
    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Generate complement edges: all unordered pairs of distinct vertices
    # that are *not* present in the original graph.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    # The target parameter is n - k.
    k_target = n - k

    return {"n": n, "edges": complement_edges, "k": k_target}

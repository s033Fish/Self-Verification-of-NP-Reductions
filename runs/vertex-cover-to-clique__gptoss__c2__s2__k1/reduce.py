"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff there exists a vertex cover of size at most k.

The target problem (Clique) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff there exists a clique of size at least k.

Standard polynomial‑time reduction:
    A set C is a vertex cover of G iff V\C is an independent set of G.
    An independent set in G is a clique in the complement graph \bar{G}.

Therefore, G has a vertex cover of size ≤ k  ⇔  \bar{G} has a clique of size
    ≥ n‑k.

The reduction constructs the complement graph of the input instance and
sets the new target parameter to n - k.

Edge‑case handling follows automatically from the parameter transformation:
    * k < 0  →  n - k > n, and Clique answers *no* for k > n.
    * k ≥ n →  n - k ≤ 0, and Clique answers *yes* for k ≤ 0.
Both behaviours match the specification of Vertex Cover.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        a Vertex Cover instance as described above.

    Returns
    -------
    dict
        A Clique instance (same ``n``) whose ``edges`` form the complement of
        the original graph and whose ``k`` is ``n - original_k``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Store original edges in a set for O(1) membership tests.
    edge_set = set()
    for u, v in original_edges:
        # Ensure the smaller vertex comes first for a canonical representation.
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Build complement edges: all unordered pairs not present in the original.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    # New k for the Clique instance.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}

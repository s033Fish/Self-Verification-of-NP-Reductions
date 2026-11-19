"""Reduction from Vertex Cover to Clique.

The source problem is Vertex Cover with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem is Clique with the same vertex set representation.

Standard polynomial‑time reduction:
    - Build the complement graph G' of the input graph G.
    - Set the new parameter k' = n - k.
    - Then G has a vertex cover of size ≤ k iff G' has a clique of size ≥ k'.

This reduction correctly handles all edge cases described in the
problem statements (negative k, k larger than n, empty edge list, etc.).
"""

from typing import List, Dict, Any


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph of an undirected graph.

    The input ``edges`` may contain each undirected edge exactly once in any
    order. The returned list will contain each missing edge exactly once with
    the lower vertex first (i.e., ``u < v``). This deterministic ordering is not
    required by the specification but makes the output stable.
    """
    # Store existing edges as a set of unordered pairs for O(1) lookup.
    existing = set()
    for u, v in edges:
        if u == v:
            # Self‑loops are not allowed by the problem definition, but we
            # ignore them gracefully.
            continue
        a, b = (u, v) if u < v else (v, u)
        existing.add((a, b))

    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary following the VertexCover instance format.

    Returns
    -------
    dict
        A dictionary following the Clique instance format such that the
        answer to the Clique instance is *yes* iff the answer to the original
        Vertex Cover instance is *yes*.
    """
    n = instance.get("n")
    edges = instance.get("edges", [])
    k = instance.get("k", 0)

    # Complement graph edges
    comp_edges = _complement_edges(n, edges)

    # New parameter for Clique
    k_prime = n - k

    return {"n": n, "edges": comp_edges, "k": k_prime}


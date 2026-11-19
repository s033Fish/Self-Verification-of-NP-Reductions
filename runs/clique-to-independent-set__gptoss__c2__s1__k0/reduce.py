"""Reduction from Clique to Independent Set.

The source problem (Clique) asks whether a given undirected graph G = (V, E)
contains a clique of size at least k.  The target problem (IndependentSet)
asks whether a graph contains an independent set of size at least k.

A classic polynomial‑time many‑one reduction is to map G to its complement
graph G̅ = (V, \overline{E}), where \overline{E} contains exactly those unordered
vertex pairs that are *not* edges of G.  A set of vertices forms a clique in G
iff it forms an independent set in G̅, and the parameter k is unchanged.

The ``reduce`` function below implements this transformation.  It receives an
instance of the source problem – a dictionary with keys ``"n"``, ``"edges"``
and ``"k"`` – and returns a dictionary in the target format with the same
``n`` and ``k`` and with ``edges`` representing the complement graph.

The implementation runs in O(n^2) time, which is polynomial in the size of the
input.  Edge cases (k ≤ 0, k > n, etc.) are preserved automatically because we
do not modify ``k`` and the vertex set stays the same.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[[int, int]], "k": int}`` – the Clique
        instance.

    Returns
    -------
    dict
        ``{"n": int, "edges": List[[int, int]], "k": int}`` – the Independent
        Set instance for the complement graph.
    """
    n: int = instance["n"]
    k: int = instance["k"]
    original_edges = instance.get("edges", [])

    # Build a set for O(1) membership tests. Store each edge as a tuple with
    # the smaller vertex first to canonicalise the undirected edge.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # Self‑loops are not allowed by the specification, but we ignore
            # them defensively.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Construct the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}


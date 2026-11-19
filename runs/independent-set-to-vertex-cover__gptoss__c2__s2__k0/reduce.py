"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a graph G = (V, E) has an
independent set of size **at least** ``k``.  The target problem (Vertex Cover)
asks whether G has a vertex cover of size **at most** ``k'``.

For any graph the complement of an independent set is a vertex cover and
vice‑versa.  Formally, S ⊆ V is independent ⇔ V \ S is a vertex cover.  Hence
``|S| ≥ k``  ⇔  ``|V| - |S| ≤ |V| - k``.  Setting ``k' = n - k`` yields an
instance of Vertex Cover that is a yes‑instance exactly when the original
Independent Set instance is a yes‑instance.

The reduction runs in linear time: we copy the number of vertices, the edge
list, and compute the new ``k`` value.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of [u, v]),
        and ``"k"`` (int) representing an Independent Set instance.

    Returns
    -------
    dict
        A dictionary in the Vertex Cover format with the same ``n`` and
        ``edges`` and ``k`` replaced by ``n - k``.
    """

    # Extract fields – we assume the input has already been validated by the
    # surrounding framework (problems.py).  Keeping the code defensive makes
    # the reducer robust if called directly.
    n: int = int(instance.get("n", 0))
    edges: List[List[int]] = list(instance.get("edges", []))
    k: int = int(instance.get("k", 0))

    # Compute the parameter for Vertex Cover.  The transformation works for
    # any integer k (including negative values) because the definitions of the
    # two problems handle those edge cases consistently.
    k_prime: int = n - k

    # Return a new instance dict.  We copy the edges list to avoid accidental
    # mutation of the caller's data.
    return {"n": n, "edges": edges, "k": k_prime}

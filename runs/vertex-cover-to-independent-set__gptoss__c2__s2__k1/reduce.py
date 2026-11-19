"""Reduction from Vertex Cover to Independent Set.

The source problem is VertexCover with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem is IndependentSet with the same graph format but a
different parameter meaning:
    "k" is the required size of an independent set (at least k).

The classic polynomial‑time reduction uses the complement relationship:
    S is a vertex cover of size ≤ k  ⇔  V\\S is an independent set of size ≥ n‑k.

Thus, given a vertex‑cover instance (G, k) we output the independent‑set
instance (G, n‑k).  All edge cases are handled automatically because the
relationship holds for any integer k (including negative values or k ≥ n).

The function ``reduce`` performs this transformation and returns a new
dictionary suitable for the TARGET problem.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        vertex‑cover instance as defined in ``problems.py``.

    Returns
    -------
    dict
        A dictionary in the IndependentSet format.  The graph (``n`` and
        ``edges``) is unchanged; the new ``k`` is ``n - original_k``.
    """
    # Extract fields; assume they are validated elsewhere.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction is simply complementing the size bound.
    new_k = n - k

    # Construct the target instance.
    return {"n": n, "edges": edges, "k": new_k}


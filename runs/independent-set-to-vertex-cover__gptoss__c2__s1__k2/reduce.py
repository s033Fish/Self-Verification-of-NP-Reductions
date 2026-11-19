"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a graph G = (V, E) has an
independent set of size at least ``k``.  The target problem (Vertex Cover) asks
whether G has a vertex cover of size at most ``k``.

It is a classic polynomial‑time many‑one reduction that uses the complement
relationship between independent sets and vertex covers:

    S is an independent set  <=>  V \ S is a vertex cover.

Consequently, G has an independent set of size ≥ k **iff** G has a vertex
cover of size ≤ |V| – k.  The reduction therefore keeps the graph unchanged and
maps the parameter ``k`` to ``|V| - k``.

The function ``reduce`` below implements this transformation.  It runs in
linear time with respect to the size of the input instance (simply copying the
edge list and performing a constant‑time arithmetic operation), which is
polynomial as required.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        An instance of the source problem with keys ``"n"``, ``"edges"`` and
        ``"k"`` as described in ``problems.py``.

    Returns
    -------
    dict
        An instance of the target problem (Vertex Cover) where the graph is
        unchanged and the new parameter ``k'`` equals ``n - k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The complement transformation: independent set size ≥ k ⇔ vertex cover
    # size ≤ n - k.
    k_prime: int = n - k

    # Return a new dictionary to avoid mutating the original instance.
    return {"n": n, "edges": edges, "k": k_prime}

"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) asks whether a given undirected graph
has a vertex cover of size at most ``k``.  The target problem (IndependentSet)
asks whether the same graph has an independent set of size at least ``k``.

The classic polynomial‑time reduction uses the complement relationship:

    S is an independent set  <=>  V \ S is a vertex cover.

Consequently, a graph G with ``n`` vertices has a vertex cover of size
``k`` iff it has an independent set of size ``n - k``.  The reduction
simply keeps the graph unchanged and maps the parameter ``k`` to
``n - k``.

The function ``reduce`` below implements this transformation.  It takes a
dictionary representing a VertexCover instance (as defined in
``problems.py``) and returns a dictionary representing an IndependentSet
instance.  The transformation runs in linear time with respect to the
size of the input instance.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A VertexCover instance with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        An IndependentSet instance with the same vertex set and edge list,
        but with the parameter transformed to ``n - k``.
    """
    # Extract fields from the source instance.  The format is guaranteed by
    # ``problems.py``; we do not perform deep validation here to keep the
    # reduction lightweight.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The target parameter is n - k.  This works for all integer values of k
    # and respects the edge‑case specifications of both problems.
    target_k: int = n - k

    # Construct the target instance.  The graph remains unchanged.
    return {"n": n, "edges": edges, "k": target_k}

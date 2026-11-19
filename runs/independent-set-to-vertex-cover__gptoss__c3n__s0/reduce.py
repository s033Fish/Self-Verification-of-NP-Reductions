"""Reduction from Independent Set to Vertex Cover.

The classical reduction uses the complement of an independent set.  For a
graph ``G = (V, E)`` and an integer ``k`` the instance ``(G, k)`` of
Independent Set is a *yes* instance iff the complement of an independent set
of size at least ``k`` is a vertex cover of size at most ``|V| - k``.  Hence the
reduction simply copies the graph and replaces ``k`` by ``|V| - k``.

The function ``reduce`` validates the source instance, constructs the target
instance and validates it before returning.  Validation ensures that the
reduction respects the exact instance format required by the benchmark.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import IndependentSet, VertexCover, InvalidInstance

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance as defined in
        ``problems.py`` – it must contain the keys ``"n"``, ``"edges"`` and
        ``"k"``.

    Returns
    -------
    dict
        A Vertex Cover instance with the same ``n`` and ``edges`` and with
        ``k' = n - k``.

    The reduction runs in linear time with respect to the size of the input
    (the list of edges) and therefore satisfies the polynomial‑time
    requirement.
    """

    # Validate the source instance.  This will raise InvalidInstance if the
    # input is malformed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Perform the classic complement reduction.
    target_k = n - k

    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges.copy(),  # shallow copy is sufficient – inner lists are immutable ints
        "k": target_k,
    }

    # Validate the produced target instance before returning it.
    VertexCover.validate(target_instance)
    return target_instance


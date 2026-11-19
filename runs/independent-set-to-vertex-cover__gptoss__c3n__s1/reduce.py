"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement of an independent set.  For a
graph ``G = (V, E)`` and an integer ``k`` the instance ``(G, k)`` of the
Independent‑Set problem is a *yes* instance iff the instance ``(G, |V|-k)``
of the Vertex‑Cover problem is a *yes* instance.  The transformation is
trivial: keep the graph unchanged and replace ``k`` with ``n - k`` where ``n``
is the number of vertices.

The function :func:`reduce` validates the source instance, performs the
transformation, validates the target instance and returns it.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import IndependentSet, VertexCover, InvalidInstance

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent‑Set instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent‑Set instance as described
        in ``problems.py`` – it must contain the keys ``"n"``, ``"edges"`` and
        ``"k"``.

    Returns
    -------
    dict
        A Vertex‑Cover instance with the same graph and ``k' = n - k``.

    Raises
    ------
    InvalidInstance
        If the supplied instance does not satisfy the Independent‑Set
        validation rules.
    """
    # Validate the source instance first – this will raise InvalidInstance on
    # malformed input.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    k: int = instance["k"]

    # The reduction is defined for any integer k.  For completeness we keep
    # the arithmetic exactly as the mathematical reduction: k' = n - k.
    target_k = n - k

    # Build the target instance.  The graph is unchanged, only the parameter
    # changes.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": [list(edge) for edge in instance["edges"]],
        "k": target_k,
    }

    # Validate the produced Vertex‑Cover instance.  This catches any bugs in
    # the construction (e.g., accidentally mutating the edge list).
    VertexCover.validate(target_instance)
    return target_instance


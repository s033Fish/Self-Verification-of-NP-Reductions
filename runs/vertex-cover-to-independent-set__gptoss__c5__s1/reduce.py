"""Reduction from Vertex Cover to Independent Set.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`IndependentSet` defined in the same file.

For a graph G = (V, E) and an integer k, a set C ⊆ V is a vertex cover of
size at most k iff its complement I = V \ C is an independent set of size at
least |V|-k. Therefore the reduction simply keeps the graph unchanged and
maps ``k`` to ``n - k``.

The function ``reduce`` validates the source instance using the source class
method, then constructs a target instance that satisfies the target
validation rules. All operations are clearly polynomial (linear) in the size
of the input.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance as described in
        ``problems.py``.  It must contain the keys ``"n"``, ``"edges"`` and
        ``"k"``.

    Returns
    -------
    dict
        A dictionary representing an Independent Set instance.  The graph is
        unchanged and the new ``k`` value is ``n - k``.

    The reduction runs in O(|V|+|E|) time and preserves the answer:
    ``instance`` is a *yes* instance of Vertex Cover iff the returned instance
    is a *yes* instance of Independent Set.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges = instance["edges"]
    k: int = instance["k"]

    # The transformed parameter for Independent Set.
    new_k = n - k

    # Build the target instance.  The graph is identical, only k changes.
    target_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": new_k}

    # Validate the target instance to ensure we didn't produce an illegal
    # instance (e.g., negative k is allowed for Independent Set).
    IndependentSet.validate(target_instance)

    return target_instance


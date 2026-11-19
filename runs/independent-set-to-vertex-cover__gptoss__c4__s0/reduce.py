"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement relationship: a set of vertices
is independent in a graph G iff its complement is a vertex cover of G.
Therefore, an instance (G, k) of Independent Set is a *yes* instance iff the
instance (G, n - k) of Vertex Cover is a *yes* instance, where n is the number
of vertices of G.

This file defines a single function ``reduce`` that takes a valid Independent
Set instance (as defined in ``problems.py``) and returns a valid VertexCover
instance with the transformed parameter.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import IndependentSet, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        graph and the required size of an independent set.

    Returns
    -------
    dict
        A new instance for the VertexCover problem. The graph is unchanged,
        and the new ``k`` is ``n - original_k``.

    The function validates the input using ``IndependentSet.validate`` and
    validates the produced output using ``VertexCover.validate``. Any
    ``InvalidInstance`` exception will propagate, signalling malformed input
    or a bug in the transformation.
    """
    # Validate the source instance first.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k_original: int = instance["k"]

    # The complement relationship: independent set of size >= k exists
    # iff vertex cover of size <= n - k exists.
    k_target: int = n - k_original

    reduced_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_target,
    }

    # Validate the produced instance to ensure it conforms to VertexCover.
    VertexCover.validate(reduced_instance)
    return reduced_instance


"""Reduction from Vertex Cover to Independent Set.

The classic reduction uses the complement relationship between vertex covers
and independent sets: a set C is a vertex cover of G iff V\\C is an independent
set of G. Consequently, G has a vertex cover of size at most k iff G has an
independent set of size at least n‑k.

This file provides a single function ``reduce`` that takes an instance of the
source problem (``VertexCover``) and returns an instance of the target problem
(``IndependentSet``) with the same graph and parameter ``k' = n - k``.

The function validates the input using the problem class' ``validate`` method
and constructs the output dictionary accordingly. The transformation runs in
linear time with respect to the size of the input instance, satisfying the
polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance. It must contain the
        keys ``"n"``, ``"edges"`` and ``"k"`` as described in ``problems.py``.

    Returns
    -------
    dict
        An IndependentSet instance with the same vertex set and edge list, but
        with ``k' = n - k``. The returned instance is guaranteed to be valid
        according to ``IndependentSet.validate``.
    """
    # Validate the source instance – will raise InvalidInstance on malformed
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the target parameter. The relationship works for all integer
    # values of k, including negative ones, because the edge‑case handling of
    # both problems aligns with this formula (see the docstrings).
    k_target: int = n - k

    reduced_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_target,
    }

    # Validate the produced instance to catch any programming errors early.
    IndependentSet.validate(reduced_instance)
    return reduced_instance


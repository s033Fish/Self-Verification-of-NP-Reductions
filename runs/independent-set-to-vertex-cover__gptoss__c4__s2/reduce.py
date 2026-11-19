"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement relationship:

    S is an independent set in G  <=>  V \ S is a vertex cover in G.

Therefore, an instance ``{n, edges, k}`` of Independent Set has a yes
answer iff the instance ``{n, edges, n - k}`` of Vertex Cover has a yes
answer.  This transformation is clearly polynomial‑time (linear in the
size of the input) and preserves the edge‑case semantics of the two
problems.

The module defines a single function ``reduce`` that takes a dictionary
representing an Independent Set instance and returns a dictionary that
conforms to the Vertex Cover specification.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import IndependentSet, VertexCover, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` that
        satisfies :class:`IndependentSet` validation.

    Returns
    -------
    dict
        A new instance for :class:`VertexCover` with the same ``n`` and
        ``edges`` but with ``k' = n - k``.

    The function runs in O(|V|+|E|) time and raises
    :class:`InvalidInstance` if the input does not conform to the source
    problem's format.
    """
    # Validate the source instance first – this also ensures the required
    # keys are present and the graph representation is well‑formed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    k: int = instance["k"]
    edges = instance["edges"]

    # Compute the complementary bound for vertex cover.
    k_target = n - k

    # Build the target instance.  The edges list can be reused directly
    # because the reduction does not modify the graph.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_target,
    }

    # Validate the produced instance against the VertexCover definition.
    # This also catches potential overflow/underflow edge cases.
    VertexCover.validate(target_instance)
    return target_instance

